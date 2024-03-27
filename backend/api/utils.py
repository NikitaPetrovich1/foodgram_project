from django.http import HttpResponse


def convert_to_txt(shopping_list):
    file_name = 'Shopping_cart.txt'
    response = HttpResponse(content_type='text/plain,charset=utf8')
    response['Content-Disposition'] = f'attachment; filename={file_name}'

    for ing in shopping_list:
        name = ing['ingredient__name']
        measurement_unit = ing['ingredient__measurement_unit']
        amount = ing['ingredient_total']
        response.write(
            (str(name) + ' - ' + str(amount)
             + ' ' + str(measurement_unit) + '\n')
        )

    return response
