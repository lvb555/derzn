from django import forms


class CustomChoiceField(forms.ChoiceField):
    def valid_value(self, value):
        """Check to see if the provided value is a valid choice."""
        text_value = str(value).lower()
        for k, v in self.choices:
            if isinstance(v, (list, tuple)):
                # This is an optgroup, so look inside the group for options
                for k2, v2 in v:
                    if value == k2 or text_value == str(k2).lower():
                        return True
            else:
                if value == k or text_value == str(k).lower():
                    return True
        return False
