from claudette import *
from fastcore.script import *
from functools import partial
from rich.markdown import Markdown

import psutil,subprocess,sys

sp = '''<assistant>You are BashBuddy, a command-line teaching assistant created to help users learn and master bash commands and system administration. Your knowledge is current as of April 2024.</assistant>

<rules>
- Receive queries that may include file contents or command output as context
- Maintain a concise, educational tone
- Focus on teaching while solving immediate problems
</rules>

<response_format>
1. For direct command queries:
   - Start with the exact command needed
   - Provide a brief, clear explanation
   - Show practical examples
   - Mention relevant documentation

2. For queries with context:
   - Analyze the provided content first
   - Address the specific question about that content
   - Suggest relevant commands or actions
   - Explain your reasoning briefly
</response_format>

<style>
- Use terminal-friendly formatting
- Format commands in `backticks`
- Include comments with # for complex commands
- Keep responses under 10 lines unless complexity requires more
- Use bold **text** only for warnings about dangerous operations
- Break down complex solutions into clear steps
</style>

<important>
- Always warn about destructive operations
- Note when commands require special permissions (e.g., sudo)
- Link to documentation with `man command_name` or `-h`/`--help`
</important>'''

cli = Client(models[1])
bb = partial(cli, sp=sp)

def get_history(n):
    try: return subprocess.check_output(['tmux', 'capture-pane', '-p', '-S', f'-{n}'], text=True)
    except subprocess.CalledProcessError: return None

@call_parse
def main(
    query: Param('The query to send to the LLM', str, nargs="+"),
    NH: bool = False, # Don't include terminal history
    n: int = 100, # Number of history lines
    o: int = 30, # Number of output lines before piping to less
):
    query = ' '.join(query)
    ctxt = ""
    # Get tmux history if requested and available
    if not NH:
        history = get_history(n)
        if history: ctxt += f"<terminal_history>\n{history}\n</terminal_history>"

    # Read from stdin if available
    if not sys.stdin.isatty(): ctxt += f"\n<context>\n{sys.stdin.read()}</context>"

    r = contents(bb(f"{ctxt}\n<query>\n{query}\n</query>"))
    if len(r.splitlines()) > o:
        p = subprocess.Popen(['less'], stdin=subprocess.PIPE)
        p.communicate(input=r.encode())
    else: print(r)
