import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from adjustText import adjust_text
import matplotlib as mpl
from matplotlib.ticker import FuncFormatter
import os

DATA_PATH = os.path.join(os.getcwd(), "Data")
SAVE_PATH = os.path.join(os.getcwd(), "Figures")

mpl.rcParams['pdf.fonttype']=42
mpl.rcParams['ps.fonttype'] = 42

def to_percentage(x, pos):
    return f'{int(x * 100)}%'

def figure_2():
    sns.set_theme(style="whitegrid")
    colors = sns.color_palette()

    data = pd.read_csv(os.path.join(DATA_PATH, "figure_2.csv"),
                       header=None, names=['Model', 'Python', 'JavaScript'])

    fontsize=16

    fig, ax = plt.subplots(figsize=(7, 5))

    n_groups = len(data)
    index = range(n_groups)
    bar_width = 0.35

    rects1 = ax.barh(index, data['Python'], bar_width, label='Python')
    rects2 = ax.barh([p + bar_width for p in index], data['JavaScript'], bar_width, label='JavaScript')

    ax.legend(fontsize=fontsize)

    ax.grid(False)  # Disable all grid lines first
    ax.xaxis.grid(True, color='darkgrey', linestyle='--', linewidth=0.5)  # Enable only horizontal grid lines

    ax.spines['top'].set_color('darkgrey')
    ax.spines['bottom'].set_color('darkgrey')
    ax.spines['left'].set_color('darkgrey')
    ax.spines['right'].set_color('darkgrey')

    ax.set_yticks([p + bar_width / 2 for p in index])
    ax.set_yticklabels(data['Model'], rotation=0, ha='right', fontsize=fontsize)

    ax.tick_params(axis='x', which='both', bottom=True, top=False, labelbottom=True)
    ax.tick_params(axis='y', which='both', left=True, right=False, labelleft=True)

    ax.tick_params(axis='y', which='major', labelsize=fontsize)

    plt.xlabel('Hallucination Rate (%)', fontsize=fontsize)

    filename = 'figure_2.pdf'
    plt.savefig(os.path.join(SAVE_PATH, filename), bbox_inches="tight", format='pdf')
    plt.show()

def figure_3():
    sns.set_theme(style="whitegrid")

    data = pd.read_csv(os.path.join(DATA_PATH, "figure_3.csv"))
    models = data['Model'].unique()

    data['Rate'] = data['Rate'].str.rstrip('%').astype(float)

    fontsize = 16

    colors = sns.color_palette("husl", len(models))
    default_palette = ["tab:blue","tab:orange","tab:green","tab:red","tab:purple"]

    g = sns.FacetGrid(data, col="Model", col_wrap=4, height=4, aspect=0.7, sharey=False, sharex=False, palette=default_palette)

    for i, (ax, model) in enumerate(zip(g.axes.flat, data['Model'].unique())):
        model_data = data[data['Model'] == model]
        sns.lineplot(ax=ax, x="Temp", y="Rate", data=model_data, marker="o", color=default_palette[i])

        # Customizing the x-axis range for each model explicitly
        if model in ['GPT 3.5', 'GPT 4 Turbo']:
            ax.grid(True, color='darkgrey', linestyle='--', linewidth=0.5)  # Enable grid lines
            ax.set_xlim(0.01, 2.00)
            ax.set_xticks([0.0, 0.50, 1.00, 1.50, 2.00])
            ax.tick_params(axis='x', which='both', bottom=True, top=False, labelbottom=True,labelsize=fontsize)
            ax.tick_params(axis='y', which='both', left=True, right=False, labelleft=True,labelsize=fontsize)
            # Adding top and right borders
            ax.spines['top'].set_visible(True)
            ax.spines['right'].set_visible(True)

        elif model in ['CodeLlama', 'DeepSeek']:
            ax.grid(True, color='darkgrey', linestyle='--', linewidth=0.5)  # Enable grid lines
            ax.set_xlim(0.01, 5.00)
            ax.set_xticks([0.0, 1, 2, 3, 4, 5])
            ax.tick_params(axis='x', which='both', bottom=True, top=False, labelbottom=True,labelsize=fontsize)
            ax.tick_params(axis='y', which='both', left=True, right=False, labelleft=True,labelsize=fontsize)
            ax.spines['top'].set_visible(True)
            ax.spines['right'].set_visible(True)

    g.add_legend()
    g.set_axis_labels("Temperature", "Hallucination Rate (%)",fontsize=fontsize)
    g.set_titles(col_template="{col_name}",size=fontsize)

    plt.subplots_adjust(top=0.9)

    filename = 'figure_3.pdf'
    plt.savefig(os.path.join(SAVE_PATH, filename), bbox_inches="tight", format='pdf')
    plt.show()

def figure_4():
    sns.set_theme(style="whitegrid")

    data = pd.read_csv(os.path.join(DATA_PATH, "figure_4.csv"),
                       header=0, names=['Model', 'Last Year', 'All-Time'])

    # Remove '%' from the values and convert them to float
    data['Last Year'] = data['Last Year'].str.rstrip('%').astype(float)
    data['All-Time'] = data['All-Time'].str.rstrip('%').astype(float)

    fontsize=16

    fig, ax = plt.subplots(figsize=(7, 5))

    n_groups = len(data)
    index = range(n_groups)
    bar_width = 0.35

    rects1 = ax.barh(index, data['Last Year'], bar_width, label='Last Year')
    rects2 = ax.barh([p + bar_width for p in index], data['All-Time'], bar_width, label='All-Time', color='#f2c45f')

    ax.legend(fontsize=fontsize)

    ax.grid(False)  # Disable all grid lines first
    ax.xaxis.grid(True, color='darkgrey', linestyle='--', linewidth=0.5)  # Enable only vertical grid lines

    ax.spines['top'].set_color('darkgrey')
    ax.spines['bottom'].set_color('darkgrey')
    ax.spines['left'].set_color('darkgrey')
    ax.spines['right'].set_color('darkgrey')

    ax.set_yticks([p + bar_width / 2 for p in index])
    ax.set_yticklabels(data['Model'], rotation=0, ha='right', fontsize=fontsize)

    plt.xlabel('Hallucination Rate (%)', fontsize=fontsize, color='black')

    ax.tick_params(axis='y', which='both', left=True, right=False, labelleft=True)
    ax.tick_params(axis='x', which='both', bottom=True, top=False, labelbottom=True)
    ax.tick_params(axis='x', which='major', labelsize=fontsize)

    filename = 'figure_4.pdf'
    plt.savefig(os.path.join(SAVE_PATH, filename), bbox_inches="tight", format='pdf')

    plt.show()

def figure_5():
    import matplotlib.ticker as mtick
    iterations_data = pd.read_csv(os.path.join(DATA_PATH, "figure_5.csv"))

    iterations_data.set_index('Model', inplace=True)

    sns.set_theme(style="whitegrid")

    fontsize = 16
    iterations_data_transposed = iterations_data.loc[:, '0':'10'].transpose()
    default_palette = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple"]

    #Convert data into percentage
    iterations_data_transposed = (iterations_data_transposed / 500) * 100

    # Plotting the grouped bar plot
    fig, ax = plt.subplots(figsize=(7, 4))
    iterations_data_transposed.plot(kind='bar', ax=ax, width=0.8, color=default_palette)

    ax.grid(False)
    ax.yaxis.grid(True, color='darkgrey', linestyle='--', linewidth=0.5)
    ax.tick_params(axis='x', which='both', bottom=True, top=False, labelbottom=True, rotation=0, labelsize=fontsize)
    ax.tick_params(axis='y', which='both', left=True, right=False, labelleft=True, labelsize=fontsize)

    #Code to format y-axis as percentage
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))

    plt.xlabel('Number of Times Hallucinated Package was Regenerated \n out of 10 trials', fontsize=fontsize)
    plt.ylabel('Percentage of Prompts', fontsize=fontsize)
    plt.legend(loc='best', fontsize=fontsize)
    #plt.tight_layout()

    filename = 'figure_5.pdf'
    plt.savefig(os.path.join(SAVE_PATH, filename), bbox_inches="tight", format='pdf')
    plt.show()

def figure_6():
    sns.set_theme(style="whitegrid")
    sns.set_palette("deep")

    data = pd.read_csv(os.path.join(DATA_PATH, "figure_6.csv"), header=0, names=['Model', 'Total Unique', 'Rate'])

    data['Rate'] = data['Rate'].str.replace('%', '').astype(float) / 100

    plt.figure(figsize=(8, 4))
    ax = sns.scatterplot(data=data, x='Total Unique', y='Rate', color='b', s=100, marker='o')

    ax.set_facecolor('white')
    ax.grid(True, color='darkgrey', linestyle='--', linewidth=0.5)
    ax.spines['top'].set_color('darkgrey')
    ax.spines['bottom'].set_color('darkgrey')
    ax.spines['left'].set_color('darkgrey')
    ax.spines['right'].set_color('darkgrey')

    texts = [plt.text(data.loc[i, 'Total Unique'], data.loc[i, 'Rate'], data.loc[i, 'Model'], ha='center', fontsize=12)
             for i in data.index]

    adjust_text(texts, iter_lim=50, time_lim=10, avoid_self=True, expand=(1.5, 2),
                arrowprops=dict(arrowstyle="->", color='b', lw=0.5), min_arrow_len=15)

    sns.regplot(data=data, x='Total Unique', y='Rate', scatter=False, color='darkorange', ax=ax)

    ax.set_xlabel('Number of Unique Package Names Generated During Testing', fontsize=16)
    ax.set_ylabel('Hallucination Rate (%)', fontsize=16)
    ax.tick_params(axis='both', which='major', labelsize=16)
    ax.yaxis.set_major_formatter(FuncFormatter(to_percentage))

    plt.tight_layout()
    filename = 'figure_6.pdf'
    plt.savefig(os.path.join(SAVE_PATH, filename), bbox_inches="tight", format='pdf')
    plt.show()

def figure_7():
    hallucination_df = pd.read_csv(os.path.join(DATA_PATH, "figure_7.csv"))

    categories = ['Valid packages from other models', 'Hallucinated packages from other models',
                  'Valid packages from same model', 'Hallucinated packages from same model']

    models = hallucination_df['Model Name']
    num_categories = len(categories)

    data = {category: hallucination_df[category].str.rstrip('%').astype(float) for category in categories}
    sns.set_theme(style="whitegrid")
    fontsize = 16

    fig, ax = plt.subplots(figsize=(8, 4))

    bar_width = 0.2
    index = range(len(models))
    colors = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple"]

    for i, category in enumerate(categories):
        ax.bar([p + bar_width * i for p in index], data[category], bar_width, label=category, color=colors[i])

    ax.set_ylabel('Accuracy (%)', fontsize=fontsize)
    ax.set_xticks([p + 1.5 * bar_width for p in index])
    ax.set_xticklabels(models)

    ax.tick_params(axis='both', which='major', labelsize=fontsize)

    short_labels = ['Valid (other model)', 'Hallucinated (other model)', 'Valid (same model)', 'Hallucinated (same model)']
    ax.legend(short_labels, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=2, fontsize=fontsize)

    ax.tick_params(axis='x', which='both', bottom=True, top=False, labelbottom=True)
    ax.tick_params(axis='y', which='both', left=True, right=False, labelleft=True)

    ax.grid(False)  # Disable all grid lines first
    ax.yaxis.grid(True, color='darkgrey', linestyle='--', linewidth=0.5)  # Enable only horizontal grid lines

    plt.tight_layout()
    filename = 'figure_7.pdf'
    plt.savefig(os.path.join(SAVE_PATH, filename), bbox_inches="tight", format='pdf')
    plt.show()

def figure_8():
    data = pd.read_csv(os.path.join(DATA_PATH, "figure_8.csv"))
    data.set_index('Number of Models', inplace=True)

    bar_width = 0.35

    fontsize = 16

    r1 = np.arange(len(data))
    r2 = [x + bar_width for x in r1]

    bar_width = 0.35

    fig, ax = plt.subplots(figsize=(7, 4))

    ax.bar(r1, data['Valid'], width=bar_width, label='Valid')
    ax.bar(r2, data['Hallucinated'], width=bar_width, label='Hallucinated')


    ax.set_yscale('log')
    y_ticks = [1, 10, 100, 1000, 10000, 100000]
    ax.set_yticks(y_ticks)

    def log_formatter(x, pos):
        return f'$10^{{{int(np.log10(x))}}}$'

    ax.yaxis.set_major_formatter(FuncFormatter(log_formatter))

    # Add labels
    plt.xlabel('No. of Models', fontsize=fontsize)
    plt.ylabel('No. of Packages', fontsize=fontsize)
    plt.xticks([r + bar_width / 2 for r in range(len(data))], data.index)

    ax.grid(False)  # Disable all grid lines first
    ax.yaxis.grid(True, color='darkgrey', linestyle='--', linewidth=0.5)  # Enable only horizontal grid lines

    ax.tick_params(axis='x', which='both', bottom=True, top=False, labelbottom=True, rotation=0, labelsize=fontsize)
    ax.tick_params(axis='y', which='both', left=True, right=False, labelleft=True, labelsize=fontsize)

    ax.legend(loc='best', ncol=2, fontsize=fontsize)

    filename = 'figure_8.pdf'
    plt.savefig(os.path.join(SAVE_PATH, filename), bbox_inches="tight", format='pdf')
    plt.show()

def figure_9():
    leven_dist_df = pd.read_csv(os.path.join(DATA_PATH, "figure_9.csv"))

    leven_dist_df.columns = ['Levenshtein Distance', 'Count']

    sns.set_theme(style="whitegrid")
    reds_palette=sns.color_palette("Spectral", as_cmap=True)

    fontsize=16

    fig, ax = plt.subplots(figsize=(7, 4))
    plt.bar(leven_dist_df['Levenshtein Distance'], leven_dist_df['Count'], color=reds_palette(np.linspace(0, 1, len(leven_dist_df))))

    y_ticks = [0, 2000, 4000, 6000, 8000, 10000]
    y_labels = ['0', '2K', '4K', '6K', '8K', '10K']

    ax.set_yticklabels([str(tick) for tick in y_ticks])
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)

    plt.xlabel('Levenshtein Distance',fontsize=fontsize)
    plt.ylabel('No. of Hallucinated Packages',fontsize=fontsize)

    ax.tick_params(axis='x', which='both', bottom=True, top=False, labelbottom=True)
    ax.tick_params(axis='y', which='both', left=True, right=False, labelleft=True)

    ax.grid(False)  # Disable all grid lines first
    ax.yaxis.grid(True, color='darkgrey', linestyle='--', linewidth=0.5)  # Enable only horizontal grid lines

    x_ticks = np.arange(0, leven_dist_df['Levenshtein Distance'].max() + 1, 5)
    plt.xticks(x_ticks, fontsize=fontsize)

    plt.yticks(fontsize=fontsize)

    plt.tight_layout()
    filename = "figure_9.pdf"
    plt.savefig(os.path.join(SAVE_PATH, filename), bbox_inches="tight", format='pdf')
    plt.show()

def figure_14():
    sns.set_theme(style="whitegrid")

    data = pd.read_csv(os.path.join(DATA_PATH, "figure_14.csv"), header=None, names=['Model', 'Percentage1', 'Percentage2'])

    data['Percentage1'] = data['Percentage1'].str.replace('%', '').astype(float)
    data['Percentage2'] = data['Percentage2'].str.replace('%', '').astype(float)

    x = data['Percentage1']
    y = data['Percentage2']

    fontsize=16

    plt.figure(figsize=(8, 4))
    ax = sns.scatterplot(x=x, y=y, data=data, color='tab:blue', s=100, marker='o')
    ax.set_facecolor('white')

    ax.grid(True, color='darkgrey', linestyle='--',linewidth=0.5)

    ax.spines['top'].set_color('darkgrey')
    ax.spines['bottom'].set_color('darkgrey')
    ax.spines['left'].set_color('darkgrey')
    ax.spines['right'].set_color('darkgrey')

    texts = []
    for i, row in data.iterrows():
        texts.append(plt.text(row['Percentage1'], row['Percentage2'], row['Model'], ha='center',fontsize=12))

    adjust_text(texts, iter_lim = 50, time_lim=10, avoid_self=True, expand=(1.5,2), arrowprops=dict(arrowstyle="->", color='b', lw=0.5), min_arrow_len=15)
    sns.regplot(x=x, y=y, data=data, scatter=False, color='tab:green', ax=ax)

    plt.xlabel('JavaScript Hallucination Rate (%)', fontsize=fontsize, color='black')
    plt.ylabel('Python Hallucination Rate (%)', fontsize=fontsize, color='black')

    ax.tick_params(axis='x', which='both', bottom=True, top=False, labelbottom=True)
    ax.tick_params(axis='y', which='both', left=True, right=False, labelleft=True)

    ax.tick_params(axis='both', which='major', labelsize=fontsize)

    filename = 'figure_14.pdf'
    plt.savefig(os.path.join(SAVE_PATH, filename), bbox_inches="tight", format='pdf')

    plt.show()

figure_2()
figure_3()
figure_4()
figure_5()
figure_6()
figure_7()
figure_8()
figure_9()
figure_14()