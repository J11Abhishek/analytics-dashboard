from django import forms


class DatasetUploadForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        f = self.cleaned_data["file"]
        if not f.name.endswith((".csv", ".xlsx", ".xls")):
            raise forms.ValidationError("Please upload a CSV or Excel file.")
        if f.size > 10 * 1024 * 1024:  # 10MB cap
            raise forms.ValidationError("File too large (max 10MB).")
        return f