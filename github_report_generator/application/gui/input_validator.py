from tkinter import messagebox


class InputValidator:
    def __init__(self, repo_entry, days_entry, token_entry):
        self.repo_entry = repo_entry
        self.days_entry = days_entry
        self.token_entry = token_entry

    def validate_all(self) -> bool:
        return (
            self._validate_repository()
            and self._validate_days()
            and self._validate_token()
        )

    def _validate_repository(self) -> bool:
        repo_name = self.repo_entry.get().strip()

        if not repo_name or "/" not in repo_name or len(repo_name.split("/")) != 2:
            messagebox.showerror(
                "\nError"
                "\nRepository name must be in format 'owner/repo'"
            )
            return False

        return True

    def _validate_days(self) -> bool:
        try:
            days = int(self.days_entry.get())
            if days <= 0:
                raise ValueError("Days must be positive")

            if days > 365:
                if not messagebox.askyesno(
                    "Warning",
                    "Analyzing more than 365 days may take a long time. Continue?",
                ):
                    return False

            return True

        except ValueError:
            messagebox.showerror("Error", "Days must be a positive number")
            return False

    def _validate_token(self) -> bool:
        # Allow empty token; unauthenticated requests may work with lower rate limits.
        return True
