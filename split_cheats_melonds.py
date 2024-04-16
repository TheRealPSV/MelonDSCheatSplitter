import xml.etree.ElementTree as ET
import os, shutil, re, asyncio
from argparse import ArgumentParser
from task_queue import FlushingTaskQueue

_sanitize_file_name_re = re.compile(r"[/\\?%*:|\"<>\x7F\x00-\x1F]")
_collapse_whitespace_re = re.compile(r"\s+")


def _build_cheat(elem: ET) -> tuple[str, str]:
    """
    Build an individual AR code given a cheat's XML element.

    Args:
        elem (xml.etree.ElementTree): an ElementTree representing an individual cheat item

    Returns:
        tuple[str, str]: a pair of strings: the first containing the name and note associated with the code; the second containing the actual value of the code (machine code numbers)
    """

    codename = ""
    codenote = ""
    codevalue = ""
    for subchild in elem:
        match subchild.tag:
            case "name":
                codename = subchild.text
            case "note":
                codenote = subchild.text
            case "codes":
                codevalue = subchild.text or ""
    key = codename
    if codenote:
        key += f" - {codenote}"
    return (key.strip(), codevalue.strip())


def _break_code_line(codeline: str) -> list[str]:
    """
    Break a string of code values on one line into individual lines containing a pair of numbers.

    Args:
        codeline (str): a string containing all the code values on a single line

    Returns:
        list[str]: a ordered list of strings with each string containing the location and value number pairs for a cheat code line
    """

    cleaned = _collapse_whitespace_re.sub(" ", codeline).strip()
    pieces = cleaned.split(" ")
    return [" ".join(pieces[i : i + 2]) for i in range(0, len(pieces), 2)]


def _sanitize_file_name(filename: str) -> str:
    """
    Sanitize a file name in case it contains illegal characters.

    Args:
        filename (str): an unsanitized filename string

    Returns:
        str: a sanitized filename string
    """

    return _sanitize_file_name_re.sub("_", filename)


async def _write_game_to_mch(elem: ET):
    """
    Convert an individual game's XML element to a MelonDS-compatible .mch cheat code file and write to disk.

    Args:
        elem (xml.etree.ElementTree): an ElementTree representing an individual game
    """

    # walk through an individual game, adding the game's meta info and cheats
    gamename = ""
    gameid = ""
    codelist = {}
    generalcodes = {}
    for child in elem:
        match child.tag:
            case "name":  # holds the game's name, meta info
                gamename = child.text
            case "gameid":  # holds the game's gameID, meta info
                gameid = child.text
            case "cheat":  # top-level cheat, save to "general" codes
                key, value = _build_cheat(child)
                generalcodes[key] = value
            case "folder":  # category of cheats, need to dig inside
                # walk through a category (folder) of cheats and add the cheats to the category list
                categoryname = ""
                subcodes = {}
                for subchild in child:
                    if subchild.tag == "name":  # holds the name of this cheat category
                        categoryname = subchild.text
                    if (
                        subchild.tag == "cheat"
                    ):  # category-level cheat, save to its category dict
                        key, value = _build_cheat(subchild)
                        subcodes[key] = value
                # once we have the list of cheats and the category name, save them to the overall cheat dict
                codelist[categoryname] = subcodes
    # if any general codes were found, add them to their own special category
    if generalcodes:
        codelist["!GENERAL"] = generalcodes

    # write the cheats to an MCH file
    with open(f"MCH/{gameid} - {_sanitize_file_name(gamename)}.mch", "w") as f:

        lines = []
        for category, codes in sorted(codelist.items()):
            lines += f"CAT {category}\n"
            lines += "\n"
            for codename, codevalue in sorted(codes.items()):
                lines += f"CODE 0 {codename}\n"
                lines += [f"{codeline}\n" for codeline in _break_code_line(codevalue)]
                lines += "\n"

        f.writelines(lines)

    # removes element from memory to save RAM once no longer necessary
    elem.clear()


async def split_xml_to_mch(threads: int):
    """Converts a cheats.xml database to a set of MelonDS-compatible .mch files.

    Args:
        threads (int): the number of simultaneous cheat entries to load and process at once.
    """

    # wipe existing folder to be safe
    if os.path.isdir("MCH"):
        shutil.rmtree("MCH")
    os.makedirs("MCH", exist_ok=True)

    # check for cheats.xml
    if not os.path.isfile("cheats.xml"):
        print(
            "ERROR: Could not find cheats.xml. Please place the cheats.xml file next to the script/program."
        )
        exit(1)

    ftq = FlushingTaskQueue(threads)

    print("Splitting, please wait...")

    # walk through xml without loading the entire thing into memory
    for event, elem in ET.iterparse("cheats.xml", events=("start", "end")):
        if event == "end" and elem.tag == "game":
            await ftq.push(_write_game_to_mch(elem))

    # final flush of queue
    await ftq.flush()


if __name__ == "__main__":
    parser = ArgumentParser(
        prog="SplitCheatsMelonDS",
        description="Split a cheats.xml file into MelonDS-compatible .mch files.",
    )
    parser.add_argument(
        "-t",
        "--threads",
        action="store",
        type=int,
        help="Optional, specify the number of threads to use when parsing. More threads will run faster, but consume more system memory and CPU cycles. Defaults to 10. If unsure, use the default.",
    )
    parser.add_argument(
        "-m",
        "--maxthreads",
        action="store_true",
        help="Optional, if specified this will process everything at once. Uses a significant amount of system memory; not recommended unless you have a lot of RAM.",
    )
    args = parser.parse_args()

    # if maxthreads is set, set taskcount to None so it has "unlimited" threads,
    #  otherwise use number of threads specified, or 10 by default
    if args.maxthreads:
        taskcount = None
    else:
        taskcount = args.threads or 10

    asyncio.run(split_xml_to_mch(taskcount))
