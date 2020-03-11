from typing import List
from typing_extensions import Final

textSync_None: Final[int] = 0
textSync_Full: Final[int] = 1
textSync_Incremental: Final[int] = 2

TextDocumentSyncKind = int

diagSev_Error: Final[int] = 1
diagSev_Warning: Final[int] = 2
diagSev_Information: Final[int] = 3
diagSev_Hint: Final[int] = 4

DiagnosticSeverity = int

diagTag_Unnecessary: Final[int] = 1
diagTag_Deprecated: Final[int] = 2

EOL: List[str] = ['\n', '\r\n', '\r']
DocumentUri = str
