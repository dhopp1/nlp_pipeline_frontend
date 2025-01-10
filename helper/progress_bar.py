import re
import time


def parse_message(text):
    "parse the progress text into progress bar value and text"
    try:
        # search terms dict
        if ("processing search terms for group" in text) or (
            "co-occurence search for group" in text
        ):
            process_dict = {
                "processing search terms for group ": {
                    "overall_step": 1,
                    "proportion": 0.00,
                    "out_text": "(1/3) processing search terms group ",
                },
                "co-occurence search for group ": {
                    "overall_step": 2,
                    "proportion": 0.33,
                    "out_text": "(2/3) finding co-occurring words for group ",
                },
                "second-level search for group ": {
                    "overall_step": 3,
                    "proportion": 0.66,
                    "out_text": "(3/3) finding second-level search terms for group ",
                },
            }
        # top words
        elif "creating word count dictionary" in text:
            process_dict = {
                "creating word count dictionary:": {
                    "overall_step": 1,
                    "proportion": 0.0,
                    "out_text": "calculating top words ",
                },
            }
        # top entities
        elif "creating entity count dictionary" in text:
            process_dict = {
                "creating entity count dictionary:": {
                    "overall_step": 1,
                    "proportion": 0.0,
                    "out_text": "calculating top entities ",
                },
            }
        # sentiment
        elif "getting sentiments" in text:
            process_dict = {
                "getting sentiments:": {
                    "overall_step": 1,
                    "proportion": 0.0,
                    "out_text": "getting sentiments ",
                },
            }
        # summary stats
        elif "getting word and sentence count" in text:
            process_dict = {
                "getting word and sentence count:": {
                    "overall_step": 1,
                    "proportion": 0.0,
                    "out_text": "getting summary statistics ",
                },
            }
        # initial converting to text
        elif ("downloading file " in text) or ("converting to text" in text):
            process_dict = {
                "downloading file ": {
                    "overall_step": 1,
                    "proportion": 0.00,
                    "out_text": "(1/2) downloading file(s): ",
                },
                "converting to text: file ": {
                    "overall_step": 2,
                    "proportion": 0.05,
                    "out_text": "(2/2) converting to text: ",
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
        try:
            next_step_proportion = process_dict[
                [
                    k
                    for k, v in process_dict.items()
                    if len([v2 for k2, v2 in v.items() if v2 == current_step + 1]) > 0
                ][0]
            ]["proportion"]
        except:
            next_step_proportion = 1.0

        overall_progress = round(
            next_step_proportion - process_dict[which_key]["proportion"], 2
        )  # overall progress available for this step

        numerator = int(re.findall(r"\d+", text.split(which_key)[1].split("/")[0])[0])
        denominator = int(text.split(which_key)[1].split("/")[1])
        addt_progress = numerator / denominator * overall_progress

        final_progress = int((base_progress + addt_progress) * 100)

        # final text
        final_text = process_dict[which_key]["out_text"] + text.split(which_key)[1]

    except:
        final_progress = 0
        final_text = ""

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
