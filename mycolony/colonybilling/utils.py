# colonybilling/utils.py

from datetime import date

def generate_receipt_number(association, model_cls):
    today_str = date.today().strftime('%Y%m%d')
    prefix = f"{association.name[:4].upper()}-RCPT"  # 4-char prefix

    filter_kwargs = {
        'receipt_number__startswith': f"{prefix}-{today_str}"
    }

    # Adjust filter depending on model type
    if model_cls.__name__ == 'PaymentRecord':
        filter_kwargs['house__association'] = association
    elif model_cls.__name__ == 'CorpusFundRecord':
        filter_kwargs['association'] = association

    last = model_cls.objects.filter(**filter_kwargs).order_by('-receipt_number').first()

    last_num = 0
    if last and last.receipt_number:
        try:
            last_num = int(last.receipt_number.split('-')[-1])
        except (IndexError, ValueError):
            pass

    return f"{prefix}-{today_str}-{last_num + 1:03d}"
