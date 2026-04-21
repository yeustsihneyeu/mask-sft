# entities for masking
taxonomy = [
    "ACCOUNTNAME",
    "ACCOUNT_NUMBER",
    "ADDRESS",
    "AMOUNT",
    "APPLICATION_NUMBER",
    "BIC",
    "BUILDINGNUMBER",
    "CITY",
    "COUNTY",
    "CREDITCARDCVV",
    "CREDITCARDISSUER",
    "CREDITCARDNUMBER",
    "CURRENCY",
    "CURRENCYCODE",
    "CURRENCYSYMBOL",
    "DATE",
    "EMAIL",
    "FIRSTNAME",
    "IBAN",
    "IP",
    "JOBTITLE",
    "LASTNAME",
    "MAC",
    "MASKEDNUMBER",
    "NAME",
    "PASSWORD",
    "PHONEIMEI",
    "PHONE_NUMBER",
    "PIN",
    "PREFIX",
    "SSN",
    "STREET",
    "STREETADDRESS",
    "USERAGENT",
    "USERNAME",
    "ZIPCODE",
]

# labels for model
label_list = ["O"] + [
    bio_label
    for entity_label in taxonomy
    for bio_label in (f"B-{entity_label}", f"I-{entity_label}")
]

label2id = {label: i for i, label in enumerate(label_list)}
id2label = {i: label for label, i in label2id.items()}


from dataclasses import dataclass
from transformers import AutoTokenizer


@dataclass
class Processor():
    tokenizer: AutoTokenizer


    def preprocess(self, example, return_label_bios: bool = False):

        """
        - tokenize text
        - get offset_mapping
        - build labels for each token by entity spans
        """

        # get text
        text = example["text"]

        # sort entities by start position
        entities = sorted(example["entities"], key=lambda x: x["start"])

        encoding = self.tokenizer(
            text,
            truncation=True,
            max_length=512,
            return_offsets_mapping=True,
        )

        offsets = encoding["offset_mapping"]
        labels = []
        label_bios = []
        current_entity_idx = None

        for offset in offsets:
            start_char, end_char = offset

            # special tokens usually have offset (0, 0)
            if start_char == end_char == 0:
                labels.append(-100)
                current_entity_idx = None
                continue

            matched_entity_idx = None

            # search entity, where it is into offset
            for idx, ent in enumerate(entities):
                ent_start = ent["start"]
                ent_end = ent["end"]

                if start_char >= ent_start and end_char <= ent_end:
                    matched_entity_idx = idx
                    break
            
            # if token is not in entity we set - O
            if matched_entity_idx is None:
                labels.append(label2id["O"])
                label_bios.append("O")
                current_entity_idx = None
            else:
                ent = entities[matched_entity_idx]
                ent_label = ent["label"]

                # if it is first token of entity
                if current_entity_idx != matched_entity_idx:
                    labels.append(label2id[f"B-{ent_label}"])
                    label_bios.append(f"B-{ent_label}")
                else:
                    labels.append(label2id[f"I-{ent_label}"])
                    label_bios.append(f"I-{ent_label}")

                current_entity_idx = matched_entity_idx

        encoding["labels"] = labels
        encoding.pop("offset_mapping")
        if return_label_bios:
            return encoding, label_bios
        return encoding
        
