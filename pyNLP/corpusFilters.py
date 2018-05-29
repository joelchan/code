journalNames =[
        "Nature",
        "Science",
        "Proceedings of the National Academy of Sciences of the United States of America",
        "Expert Syst.Appl.",
        "IEEE Communications Letters"
    ]

filterStrings =["brain",
    "neuro",
    "cog",
    "psychol",
    "comput",
    "acm",
    "sigchi",
    "interaction",
    "cscw",
    "info",
    "visualization",
    "learning",
    "statisti",
    "design",
    "user",
    "interface",
    "behavior",
    "social",
    "creativ",
    "software"]

def filterByJournal(article):
    if article["journalName"] in journalNames:
        return True

    for strToMatch in filterStrings:
        if strToMatch in article["journalName"]:
            return True

    return False