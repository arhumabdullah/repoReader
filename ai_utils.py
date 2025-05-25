import openai

openai.api_key = "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"

def get_explanation(test_name, value, value_range, unit):
    """
    Use OpenAI's GPT-3.5 to explain test results in simple terms.
    
    Parameters:
        test_name (str): The name of the test (e.g., Hemoglobin, Glucose).
        value (float): The measured value of the test.
        value_range (str): The normal range for the test (e.g., '13-17' for Hemoglobin).
        unit (str): The unit of measurement for the test (e.g., 'g/dL').

    Returns:
        str: A simple explanation of the test result.
    """
    prompt = (
        f"Explain in simple language what it means if the patient's {test_name} is {value} {unit}, "
        f"given the normal range is {value_range}."
    )
    
    try:
        response = openai.completions.create(
            model="gpt-3.5-turbo",  
            prompt=prompt,
            max_tokens=150,
            temperature=0.7
        )
        
        explanation = response['choices'][0]['text'].strip()
        return explanation

    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return "Unable to provide an explanation at the moment."

def analyze_value(value, normal_range):
    """
    Categorize the test result based on the normal range and provide advice.
    
    Parameters:
        value (float): The measured value of the test.
        normal_range (str): The normal range for the test (e.g., '13-17' for Hemoglobin).

    Returns:
        tuple: A tuple containing the result status (Low/Normal/High) and advice for follow-up.
    """
    low, high = map(float, normal_range.split('-'))
    
    if value < low:
        return "Low", "Consider seeing a doctor or improving your diet."
    elif value > high:
        return "High", "Talk to a doctor about this high result."
    else:
        return "Normal", "Everything looks okay here!"
