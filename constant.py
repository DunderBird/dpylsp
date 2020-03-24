from typing import List

textSync_None = 0
textSync_Full = 1
textSync_Incremental = 2

TextDocumentSyncKind = int

diagSev_Error = 1
diagSev_Warning = 2
diagSev_Information = 3
diagSev_Hint = 4

DiagnosticSeverity = int

diagTag_Unnecessary = 1
diagTag_Deprecated = 2

EOL: List[str] = ['\n', '\r\n', '\r']
DocumentUri = str

MessageType = int

message_error = 1
message_warning = 2
message_info = 3
message_log = 4
