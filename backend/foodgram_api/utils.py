from django.http import HttpResponse


def convert_shopping_cart_to_txt(shopping_list):
    file_name = 'Shopping_cart.txt'
    response = HttpResponse(content_type='text/plain,charset=utf8')
    response['Content-Disposition'] = f'attachment; filename={file_name}'

    for ingredient in shopping_list:
        name = ingredient['ingredient__name']
        measurement_unit = ingredient['ingredient__measurement_unit']
        amount = ingredient['ingredient_total']
        response.write(
            (str(name) + ' - ' + str(amount)
             + ' ' + str(measurement_unit) + '\n')
        )

    return response
