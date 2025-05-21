import re
from typing import Optional
from pydantic import BaseModel, Field
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

class PIIFilter:
    class Valves(BaseModel):
        priority: int = Field(
            default=0, description="Priority level for the filter operations."
        )
        enabled_for_admins: bool = Field(
            default=True,
            description="Whether PII Redaction is enabled for admin users.",
        )
        # Engine selection
        use_presidio: bool = Field(
            default=False, description="Use Presidio engine for PII detection"
        )
        use_regex: bool = Field(
            default=True, description="Use regex patterns for PII detection"
        )
        # Presidio settings
        presidio_entities: str = Field(
            default="PERSON,EMAIL_ADDRESS,PHONE_NUMBER,US_SSN,CREDIT_CARD,IP_ADDRESS,US_PASSPORT,LOCATION,DATE_TIME,NRP,MEDICAL_LICENSE,URL",
            description="Comma-separated list of Presidio entity types to redact",
        )
        presidio_language: str = Field(
            default="en", description="Language code for Presidio analyzer"
        )
        # Regex settings
        redact_email: bool = Field(default=True, description="Redact email addresses")
        redact_phone: bool = Field(default=True, description="Redact phone numbers")
        redact_account_number: bool = Field(default=True, description="Redact Account Numbers")
        redact_pancard: bool = Field(default=True, description="Redact Pancard numbers")
        redact_dob: bool = Field(default=True, description="Redact Date of Birth")

    def __init__(self):
        self.file_handler = False
        self.valves = self.Valves()
        self.patterns = {
            "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            "phone": re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"),
            "account_number": re.compile(r"\b\d{10,17}\b"), 
            "pancard": re.compile(r"\b[A-Z]{5}\d{4}[A-Z]{1}\b"),
            "dob": re.compile(r"\b(?:\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2})\b"),
        }
        self._analyzer = None
        self._anonymizer = None

    @property
    def analyzer(self):
        if self._analyzer is None:
            self._analyzer = AnalyzerEngine()
        return self._analyzer

    @property
    def anonymizer(self):
        if self._anonymizer is None:
            self._anonymizer = AnonymizerEngine()
        return self._anonymizer

    def redact_with_presidio(self, text: str) -> str:
        entities = [
            entity.strip() for entity in self.valves.presidio_entities.split(",")
        ]

        results = self.analyzer.analyze(
            text=text, language=self.valves.presidio_language, entities=entities
        )

        anonymized_text = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators={ 
                "DEFAULT": OperatorConfig("replace", {"new_value": "[REDACTED]"}), 
            },
        )

        return anonymized_text.text

    def redact_with_regex(self, text: str) -> str:
        if self.valves.redact_email:
            text = self.patterns["email"].sub("[EMAIL REDACTED]", text)
        if self.valves.redact_phone:
            text = self.patterns["phone"].sub("[PHONE REDACTED]", text)
        if self.valves.redact_account_number:
            text = self.patterns["account_number"].sub("[ACCOUNT NUMBER REDACTED]", text)
        if self.valves.redact_pancard:
            text = self.patterns["pancard"].sub("[PANCARD REDACTED]", text)
        if self.valves.redact_dob:
            text = self.patterns["dob"].sub("[DOB REDACTED]", text)
        return text

