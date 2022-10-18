from django import forms

BREAKS = (
    ("A", "Now"),
    ("B", "First Break"),
    ("C", "Second Break"),
    ("D", "LAst Break"),
)


class LoginForm(forms.Form):
    name = forms.CharField(label="Your name", max_length=100)


class OrderForm(forms.Form):
    item_name = forms.CharField(
        label="Item | Price/unit", widget=forms.Select(choices=BREAKS)
    )
    quantity = forms.IntegerField(label="Quantity")
