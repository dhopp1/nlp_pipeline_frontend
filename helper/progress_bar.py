import time


def parse_message(text):
    "parse the progress text into progress bar value and text"
    process_dict = {
        "downloading file ": {
            "overall_step": 1,
            "proportion": 0.00,
            "out_text": "(1/7) downloading file(s): ",
        },
        "converting to text: file ": {
            "overall_step": 2,
            "proportion": 0.1,
            "out_text": "(2/7) converting to text: ",
        },
        "Populating vector database (1/5), reading documents ": {
            "overall_step": 3,
            "proportion": 0.2,
            "out_text": "(3/7) reading documents: ",
        },
        "Populating vector database (2/5), chunking documents ": {
            "overall_step": 4,
            "proportion": 0.22,
            "out_text": "(4/7) chunking documents: ",
        },
        "Populating vector database (3/5), adding nodes ": {
            "overall_step": 5,
            "proportion": 0.24,
            "out_text": "(5/7) adding nodes (1/2): ",
        },
        "Populating vector database (4/5), adding nodes ": {
            "overall_step": 6,
            "proportion": 0.29,
            "out_text": "(6/7) adding nodes (2/2): ",
        },
        "Populating vector database (5/5), adding nodes to vector store": {
            "overall_step": 7,
            "proportion": 0.98,
            "out_text": "(7/7) adding nodes to vector store",
        },
    }
    which_key = [x for x in process_dict.keys() if x in text]
    if len(which_key) > 0:
        which_key = which_key[0]
    else:
        return 0, "?"
    base_progress = process_dict[which_key]["proportion"]

    # overall progress available for this step
    current_step = process_dict[which_key]["overall_step"]
    next_step_proportion = process_dict[
        [
            k
            for k, v in process_dict.items()
            if len([v2 for k2, v2 in v.items() if v2 == current_step + 1]) > 0
        ][0]
    ]["proportion"]

    overall_progress = round(
        next_step_proportion - process_dict[which_key]["proportion"], 2
    )  # overall progress available for this step

    if process_dict[which_key]["overall_step"] != 7:
        numerator = int(text.split(which_key)[1].split("/")[0])
        denominator = int(text.split(which_key)[1].split("/")[1])
        addt_progress = numerator / denominator * overall_progress
    else:
        addt_progress = 0

    final_progress = int((base_progress + addt_progress) * 100)

    # final text
    final_text = process_dict[which_key]["out_text"] + text.split(which_key)[1]

    return final_progress, final_text


class Logger(object):
    def __init__(self, status_progress, status_text):
        self.buffer = ""
        self.status_progress = status_progress
        self.status_text = status_text
        self.last_update = 0

    def write(self, message):
        # only write once per second
        if time.time() - self.last_update >= 1:
            progress_update, text_update = parse_message(message)
            if text_update != "?":
                self.status_progress = self.status_progress.progress(progress_update)
                self.status_text = self.status_text.markdown(text_update)
            self.last_update = time.time()

    def flush(self):
        pass

    def clear(self):
        self.status_progress = self.status_progress.empty()
        self.status_text = self.status_text.empty()
