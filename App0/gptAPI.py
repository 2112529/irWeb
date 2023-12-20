import requests
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"])
def ask_question(request):
    context = {}
    if request.method == 'POST':
        user_question = request.POST.get('question', '')
        answer = get_gpt3_answer(user_question)
        context['question'] = user_question
        context['answer'] = answer

    return render(request, 'gptAPI.html', context)

def get_gpt3_answer(question):
    try:
        response = requests.post(
            'https://api.openai.com/v1/engines/davinci/completions',
            headers={
                'Authorization': 'Bearer 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',
                'Content-Type': 'application/json'
            },
            json={
                'prompt': question,
                'max_tokens': 150
            }
        )
        response.raise_for_status()  # 这将在发生 HTTP 错误时抛出异常
        return response.json()['choices'][0]['text'].strip()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # 打印 HTTP 错误
    except Exception as err:
        print(f"Other error occurred: {err}")  # 打印其他错误
    return "Unable to get an answer at this time."

