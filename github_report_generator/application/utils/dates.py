from datetime import datetime, timedelta


def calculate_date_range(args) -> tuple[datetime, datetime]:
    if getattr(args, "days", None):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.days)
    else:
        # First day of the specified month/year
        start_date = datetime(args.year, args.month, 1)
        # First day of the next month
        if args.month == 12:
            end_date = datetime(args.year + 1, 1, 1)
        else:
            end_date = datetime(args.year, args.month + 1, 1)

    if getattr(args, "debug", False):
        print(f"Date range: {start_date} to {end_date}")

    return start_date, end_date
