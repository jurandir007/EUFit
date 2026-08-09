# app/ml/TLR.py

def calculate_trend_line(dates, values):
    """
    Applies Linear Regression using index positions as X 
    to match Chart.js category scale and guarantee a straight line.
    """
    if not dates or not values or len(dates) != len(values) or len(dates) < 2:
        return []

    # Use index positions (0, 1, 2, ...) as X to match chart category spacing
    timestamps = list(range(len(dates)))

    n = len(timestamps)
    sum_x = sum(timestamps)
    sum_y = sum(values)
    sum_xy = sum(x * y for x, y in zip(timestamps, values))
    sum_x2 = sum(x ** 2 for x in timestamps)

    # Prevent division by zero error
    denominator = (n * sum_x2 - sum_x ** 2)
    if denominator == 0:
        return []

    # Linear Regression Formulas (y = mx + b)
    m = (n * sum_xy - sum_x * sum_y) / denominator
    b = (sum_y - m * sum_x) / n

    # Generate the projected linear points
    trend_line = [round((m * x + b), 2) for x in timestamps]
    return trend_line
