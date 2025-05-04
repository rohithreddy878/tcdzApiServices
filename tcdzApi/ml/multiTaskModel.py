from torch import nn
from transformers import AutoModelForSequenceClassification

class MultiTaskModel(nn.Module):
    def __init__(self, base_model_name, num_line_labels, num_length_labels):
        super(MultiTaskModel, self).__init__()
        self.base_model = AutoModelForSequenceClassification.from_pretrained(base_model_name, num_labels=1)  # Match training
        self.dropout = nn.Dropout(0.1)
        self.classifier_line = nn.Linear(self.base_model.config.hidden_size, num_line_labels)
        self.classifier_length = nn.Linear(self.base_model.config.hidden_size, num_length_labels)

    def forward(self, input_ids, attention_mask, labels_line=None, labels_length=None):
        outputs = self.base_model.base_model(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.last_hidden_state[:, 0]  # CLS token
        pooled_output = self.dropout(pooled_output)

        logits_line = self.classifier_line(pooled_output)
        logits_length = self.classifier_length(pooled_output)

        loss = None
        if labels_line is not None and labels_length is not None:
            loss_fn = nn.CrossEntropyLoss()
            loss_line = loss_fn(logits_line, labels_line)
            loss_length = loss_fn(logits_length, labels_length)
            loss = loss_line + loss_length

        return {"loss": loss, "logits_line": logits_line, "logits_length": logits_length}
