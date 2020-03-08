from typing import Optional
from dpylsp import LspItem
from text import Range
import constant as ct


class Diagnostic(LspItem):
    def __init__(self,
                 range: Range,
                 message: str,
                 severity: Optional[ct.DiagnosticSeverity] = None,
                 **kwargs):
        self.range = range
        self.message = message
        self.severity = severity
