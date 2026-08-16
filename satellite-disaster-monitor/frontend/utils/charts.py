import matplotlib.pyplot as plt

def generate_sample_chart():
    fig, ax = plt.subplots()
    ax.bar(['Normal', 'Affected'], [80, 20])
    return fig
