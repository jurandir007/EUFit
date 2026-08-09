# app/ml/m_average.py

def calculate_moving_average(data, window_size=7):
    """
    Calculates the moving average of a list of values.
    """
    if not data or len(data) < window_size:
        return []
    
    ma_data = []
    for i in range(len(data)):
        if i < window_size - 1:
            # Keep empty (None) until the window size is reached
            ma_data.append(None)
        else:
            window = data[i - window_size + 1 : i + 1]
            ma_data.append(round(sum(window) / window_size, 2))
            
    return ma_data
