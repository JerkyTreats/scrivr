class ProcessingRule:
    pass


class RemoveDuplicateEmptyLinesRule(ProcessingRule):
    def process(self, text):
        return "\n".join(filter(lambda x: x.strip(), text.split("\n")))
