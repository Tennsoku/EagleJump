import re

caps = "([A-Z])"
nums = "([0-9])"
lowercases = "([a-z])"
prefixes = "(Mr|Mrs|Dr)[.]"

def split_sentence(filename):
    text = open(filename).read()
    text = " " + text + "  "
    text = text.replace("\n", " ")
    text = re.sub(prefixes, "\\1<period>", text)
    text = re.sub("[.]" + nums, "<period>\\1", text)
    text = re.sub("[.]" + " " + lowercases, "<period> \\1", text)
    # text = re.sub("[.]" + "[.]", " <period>.", text)
    if "!" in text: text = text.replace("!\"", "\"!")
    if "?" in text: text = text.replace("?\"", "\"?")
    text = text.replace(". ", ".<stop>")
    text = text.replace("? ", "?<stop>")
    text = text.replace("! ", "!<stop>")
    text = text.replace("<period>", ".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    f = open("q5.out","w")
    for sentence in sentences:
        f.write(sentence)
        f.write("\n")
    f.close()
    print sentences
    return sentences

# split_sentence("text.txt")
