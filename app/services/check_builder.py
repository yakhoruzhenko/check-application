import os
import textwrap

from app.models.checks import Check


def built_text_representation(check: Check) -> str:
    LINE_LENGTH = int(os.getenv('CHECK_LINE_LENGTH', 40))
    LEFT_SIDE_MAX_LENGTH = int(LINE_LENGTH * 0.7)
    RIGHT_SIDE_MAX_LENGTH = LINE_LENGTH - LEFT_SIDE_MAX_LENGTH
    check_lines = []

    # Header
    check_creator_name = f'{check.creator.name}'
    wrapped_creator_name = textwrap.fill(check_creator_name, width=LINE_LENGTH)
    wrapped_lines = wrapped_creator_name.splitlines()
    for line in wrapped_lines:
        check_lines.append(line.center(LINE_LENGTH))
    check_lines.append('=' * LINE_LENGTH)

    # Items
    for i, item in enumerate(check.items):
        check_lines.append(f'{item.quantity:.2f} x {item.price:.2f}')
        wrapped_title = textwrap.fill(item.title, width=LEFT_SIDE_MAX_LENGTH)
        wrapped_lines = wrapped_title.splitlines()
        for j, line in enumerate(wrapped_lines):
            if j == len(wrapped_lines) - 1:  # Last line gets the amount appended
                check_lines.append(f'{line:<{LEFT_SIDE_MAX_LENGTH}}{item.amount:>{RIGHT_SIDE_MAX_LENGTH}}')
            else:
                check_lines.append(f'{line:<{LEFT_SIDE_MAX_LENGTH}}')
        # Add separator except for the last item
        if i < len(check.items) - 1:
            check_lines.append('-' * LINE_LENGTH)

    # Totals
    check_lines.append('=' * LINE_LENGTH)
    check_lines.append(f'{"TOTAL":<{LEFT_SIDE_MAX_LENGTH}}{check.total_amount:>{RIGHT_SIDE_MAX_LENGTH}.2f}')
    check_lines.append(
        f'{check.payment_method.capitalize():<{LEFT_SIDE_MAX_LENGTH}}{check.paid_amount:>{RIGHT_SIDE_MAX_LENGTH}.2f}'
    )
    check_lines.append(f'{"Change":<{LEFT_SIDE_MAX_LENGTH}}{check.change:>{RIGHT_SIDE_MAX_LENGTH}.2f}')
    check_lines.append('=' * LINE_LENGTH)

    # Footer
    check_lines.append(check.created_at.strftime('%d.%m.%Y %H:%M').center(LINE_LENGTH))
    check_lines.append('Thank you for your purchase!'.center(LINE_LENGTH))
    return '\n'.join(check_lines)

# TODO: consider building HTML representations
