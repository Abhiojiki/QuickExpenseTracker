"""Data models for the Transaction app.

Contains two lightweight models:
- Category: a small lookup table for transaction categories
- Transaction: stores a user's monetary entries with optional image and description

All fields are simple Django fields; behaviour notes are kept on fields and
the __str__ implementations.
"""

from django.db import models


account_types = (("income", "income"), ("expense", "expense"))


class Category(models.Model):
    """A category for transactions.

    Fields
    - name: human readable name
    - type: one of `income` or `expense` used to categorize transaction nature
    """
    name = models.CharField(max_length=100)
    type = models.CharField(choices=account_types, default="expense", max_length=10)

    def __str__(self):
        """Return the human-readable name for administration and display."""
        return self.name


class Transaction(models.Model):
    """A monetary transaction belonging to a user.

    Fields
    - user: ForeignKey to the auth user who owns the transaction
    - added_on: timestamp set when the row is created
    - amount: float amount (positive numbers expected)
    - category: FK to `Category`
    - date: the date the transaction applies to
    - image: optional image (e.g., receipt)
    - description: free-text description

    Notes
    - `__str__` returns the first token of the description for brevity in lists.
    - Meta.ordering sorts by `-date` (most recent first).
    """
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="transactions")
    added_on = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.DateField()
    image = models.ImageField(upload_to="images", null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        """Short representation used in admin and lists."""
        return str(self.description.split(" ")[0])

    class Meta:
        ordering = ['-date']


