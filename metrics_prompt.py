import sys
import os
import matplotlib.pyplot as plt


def prompt_int(message: str, default: int | None = None) -> int:
    while True:
        try:
            raw = input(message).strip()
            if raw == '' and default is not None:
                return default
            value = int(raw)
            if value < 0:
                print('Введите неотрицательное целое число.')
                continue
            return value
        except ValueError:
            print('Введите целое число, пожалуйста.')


def safe_div(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def main():
    print('=== Подсчёт метрик (конфузионная матрица a,b,c,d) ===')
    print('Интерпретация:')
    print('  a — TP (True Positive): релевантные найденные системой')
    print('  b — FP (False Positive): нерелевантные, но показанные системой')
    print('  c — FN (False Negative): релевантные, но не найденные системой')
    print('  d — TN (True Negative): нерелевантные и не показанные системой')
    print('\nПодсказка:')
    print('  Первая страница — количество найденных системой документов (ссылок).')
    print('  Вторая страница — количество документов, которые система не нашла.')
    print('  Эти числа служат проверкой: a + b = найдено; c + d = не найдено.')
    print('  Если они не совпадут, мы просто выведем предупреждение.\n')

    found_count = prompt_int('Сколько ссылок на 1-й странице (найдено системой)? ', default=None)
    not_found_count = prompt_int('Сколько ссылок на 2-й странице (не найдены системой)? ', default=None)

    print('\nВведите значения a, b, c, d:')
    a = prompt_int('a (TP): ')
    b = prompt_int('b (FP): ')
    c = prompt_int('c (FN): ')
    d = prompt_int('d (TN): ')

    # Валидация консистентности с подсказочными суммами
    if found_count is not None and (a + b) != found_count:
        print(f'ВНИМАНИЕ: a + b = {a + b}, но на 1-й странице указано {found_count}.')
    if not_found_count is not None and (c + d) != not_found_count:
        print(f'ВНИМАНИЕ: c + d = {c + d}, но на 2-й странице указано {not_found_count}.')

    total = a + b + c + d
    retrieved = a + b
    relevant = a + c

    precision = safe_div(a, a + b)  # точность: из показанных, сколько релевантных
    recall = safe_div(a, a + c)     # полнота: из релевантных, сколько нашли
    f1 = safe_div(2 * precision * recall, precision + recall) if (precision + recall) > 0 else 0.0

    accuracy = safe_div(a + d, total)
    error_rate = 1.0 - accuracy

    specificity = safe_div(d, b + d)       # True Negative Rate
    fallout = safe_div(b, b + d)            # False Positive Rate (1 - specificity)
    npv = safe_div(d, c + d)                # Negative Predictive Value
    fnr = safe_div(c, a + c)                # False Negative Rate (1 - recall)

    print('\n=== Результаты ===')
    print(f'Всего документов (N): {total}')
    print(f'Показано системой (a+b): {retrieved}')
    print(f'Всего релевантных (a+c): {relevant}')

    print('\nКлассические метрики ИИР/классификации:')
    print(f'- Precision (точность): {precision:.4f}  — из показанных системой документов доля релевантных. Формула: a/(a+b)')
    print(f'- Recall (полнота):    {recall:.4f}  — из всех релевантных документов доля найденных системой. Формула: a/(a+c)')
    print(f'- F1:                  {f1:.4f}  — гармоническое среднее precision и recall. Формула: 2PR/(P+R)')
    print(f'- Accuracy (точность классификации): {accuracy:.4f}  — доля верных решений. Формула: (a+d)/(a+b+c+d)')
    print(f'- Error rate (ошибка):               {error_rate:.4f}  — доля ошибок. Формула: 1-accuracy')

    print('\nДополнительные метрики:')
    print(f'- Specificity (TNR): {specificity:.4f}  — доля правильно отвергнутых нерелевантных: d/(b+d)')
    print(f'- Fallout (FPR):     {fallout:.4f}  — доля ложных срабатываний среди нерелевантных: b/(b+d)')
    print(f'- NPV:               {npv:.4f}  — доля истинно отрицательных среди всех отрицательных: d/(c+d)')
    print(f'- FNR:               {fnr:.4f}  — доля пропусков среди релевантных: c/(a+c)')

    print('\nПояснение:')
    print('- Precision отвечает на вопрос: "Если система показала, можно ли этому верить?"')
    print('- Recall отвечает на вопрос: "Нашла ли система большую часть релевантных документов?"')
    print('- F1 балансирует между precision и recall, когда важны оба аспекта.')
    print('- Accuracy полезна при сбалансированных классах, но в ИИР часто малоинформативна.')
    print('- Specificity/FPR важны, когда критично не показывать нерелевантное.')

    # Графики
    out_dir = 'data'
    os.makedirs(out_dir, exist_ok=True)

    # 1) Тепловая карта матрицы ошибок
    fig, ax = plt.subplots(figsize=(4, 4))
    mat = [[a, b], [c, d]]
    im = ax.imshow(mat, cmap='Blues')
    for (i, j), val in [((0,0), a), ((0,1), b), ((1,0), c), ((1,1), d)]:
        ax.text(j, i, str(val), va='center', ha='center', color='black', fontsize=12)
    ax.set_xticks([0,1]); ax.set_yticks([0,1])
    ax.set_xticklabels(['Релевант', 'Нерелевант'])
    ax.set_yticklabels(['Показан', 'Не показан'])
    ax.set_title('Матрица ошибок (a,b,c,d)')
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cm_path = os.path.join(out_dir, 'confusion_matrix.png')
    plt.tight_layout(); plt.savefig(cm_path, dpi=150); plt.close()

    # 2) Столбцы метрик
    names = ['Precision', 'Recall', 'F1', 'Accuracy', 'Specificity', 'FPR', 'NPV', 'FNR']
    values = [precision, recall, f1, accuracy, specificity, fallout, npv, fnr]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(names, values, color='#416868')
    ax.set_ylim(0, 1.05)
    ax.set_title('Метрики качества')
    for i, v in enumerate(values):
        ax.text(i, v + 0.02 if v <= 0.95 else 0.97, f'{v:.2f}', ha='center', fontsize=9)
    plt.xticks(rotation=20)
    bars_path = os.path.join(out_dir, 'metrics_bars.png')
    plt.tight_layout(); plt.savefig(bars_path, dpi=150); plt.close()

    # 3) ROC-плоскость (точка)
    tpr = recall
    fpr = fallout
    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    ax.plot([0,1], [0,1], '--', color='#999', label='случайно')
    ax.scatter([fpr], [tpr], color='#771616', label=f'TPR={tpr:.2f}, FPR={fpr:.2f}')
    ax.set_xlabel('FPR (False Positive Rate)')
    ax.set_ylabel('TPR (Recall)')
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.set_title('ROC (одна точка)')
    ax.legend(loc='lower right')
    roc_path = os.path.join(out_dir, 'roc_point.png')
    plt.tight_layout(); plt.savefig(roc_path, dpi=150); plt.close()

    print('\nСохранены графики:')
    print(f'- {cm_path}')
    print(f'- {bars_path}')
    print(f'- {roc_path}')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nОтменено пользователем.')
        sys.exit(1)


