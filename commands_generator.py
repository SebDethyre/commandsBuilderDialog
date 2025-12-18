import subprocess
import json
import re

def get_man_options(command):
    try:
        output = subprocess.check_output(['man', command], stderr=subprocess.DEVNULL, text=True)
    except Exception:
        return []

    lines = output.splitlines()
    options = []

    seen_flags = set()

    for line in lines:
        match = re.match(r'\s{0,5}(-\w|--[a-zA-Z0-9-]+)([, ]+(-\w|--[a-zA-Z0-9-]+))?\s*(<[^>]+>|[A-Z]+)?\s+-\s+(.*)', line)
        if match:
            flag1 = match.group(1)
            flag2 = match.group(3)
            arg = match.group(4)
            desc = match.group(5)

            flag = flag1
            if flag2:
                flag += f" {flag2}"

            if flag in seen_flags:
                continue
            seen_flags.add(flag)

            opt = {
                "label": desc.split('.')[0].capitalize(),
                "flag": flag.strip()
            }

            # Heuristique basique : si option demande un argument → text, sinon checkbox
            if arg or "<" in desc or "PATH" in desc.upper() or "FILE" in desc.upper():
                opt["type"] = "text"
                if "PATH" in desc.upper() or "FILE" in desc.upper():
                    opt["flag"] = "path"
            else:
                opt["type"] = "checkbox"

            options.append(opt)

    return options


def build_commands_json(commands_list, output_file="commands.json"):
    all_commands = {}
    for cmd in commands_list:
        print(f"Parsing: {cmd}")
        opts = get_man_options(cmd)
        if opts:
            all_commands[cmd] = {"options": opts}

    with open(output_file, "w") as f:
        json.dump(all_commands, f, indent=2, ensure_ascii=False)

    print(f"\n✅ JSON enregistré dans: {output_file}")


if __name__ == "__main__":
    # Exemples basiques, à adapter ou compléter
    common_commands = [
        "ls", "grep", "find", "tar", "curl", "wget", "cp", "mv", "rm", "ps", "top",
        "cat", "echo", "df", "du", "head", "tail", "chmod", "chown", "kill"
    ]
    build_commands_json(common_commands)
