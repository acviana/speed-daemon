import matplotlib.pyplot as plt


def plot_histogram(
    ax,
    data,
    bins,
    orientation="vertical",
    mean=None,
    std=None,
    y_label=None,
    x_label=None,
    y_scale="linear",
):
    ax.hist(data, bins=bins, orientation=orientation)
    if orientation == "vertical":
        ax.axvline(mean - std, linestyle=":")
        ax.axvline(mean, linestyle="--")
        ax.axvline(mean + std, linestyle=":")
    else:
        ax.axhline(mean - std, linestyle=":")
        ax.axhline(mean, linestyle="--")
        ax.axhline(mean + std, linestyle=":")
    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    ax.set_yscale(y_scale)


def plot_histograms(df, stats):
    bins = 25
    fig, axs = plt.subplots(3, 2)
    fig.tight_layout(pad=1.0)

    plot_histogram(
        ax=axs[0][0],
        data=df["download_mbps"],
        bins=bins,
        mean=stats["download_mbps"]["mean"],
        std=stats["download_mbps"]["std"],
        y_label="Downloads",
        x_label="Mbps",
    )
    plot_histogram(
        ax=axs[1][0],
        data=df["upload_mbps"],
        bins=bins,
        mean=stats["upload_mbps"]["mean"],
        std=stats["upload_mbps"]["std"],
        y_label="Upload",
        x_label="Mbps",
    )
    plot_histogram(
        ax=axs[2][0],
        data=df["ping"],
        bins=bins,
        mean=stats["ping"]["mean"],
        std=stats["ping"]["std"],
        y_label="Ping",
        x_label="ms",
    )

    plot_histogram(
        ax=axs[0][1],
        data=df["download_mbps"],
        bins=bins,
        mean=stats["download_mbps"]["mean"],
        std=stats["download_mbps"]["std"],
        x_label="Mbps",
        y_scale="log",
    )
    plot_histogram(
        ax=axs[1][1],
        data=df["upload_mbps"],
        bins=bins,
        mean=stats["upload_mbps"]["mean"],
        std=stats["upload_mbps"]["std"],
        x_label="Mbps",
        y_scale="log",
    )
    plot_histogram(
        ax=axs[2][1],
        data=df["ping"],
        bins=bins,
        mean=stats["ping"]["mean"],
        std=stats["ping"]["std"],
        x_label="ms",
        y_scale="log",
    )

    return fig


def plot_mean_median_std(ax, data, data_type):
    ax.errorbar(data.index, "mean", yerr="std", marker="o", linestyle="", data=data)
    ax.plot(data.index, "median", marker="x", linestyle="", data=data)
    ax.set_title(data_type)
    if data_type in ["Download", "Upload"]:
        ax.set_ylabel("Mbps")
    elif data_type == "Ping":
        ax.set_ylabel("ms")


def plot_timeseries_summary(df):
    fig, axs = plt.subplots(3, 1)
    fig.tight_layout(pad=1.0)

    plot_mean_median_std(axs[0], df["download_mbps"], "Download")
    plot_mean_median_std(axs[1], df["upload_mbps"], "Upload")
    plot_mean_median_std(axs[2], df["ping"], "Ping")

    fig.autofmt_xdate()

    return fig


def plot_scatterplot(ax, x_data, y_data, mean, std, title, y_label, x_label=None):
    ax.plot(x_data, y_data, ".")
    ax.axhline(mean - std, linestyle=":")
    ax.axhline(mean, linestyle="--")
    ax.axhline(mean + std, linestyle=":")
    ax.set_title(title)
    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)


def plot_summary(df, stats):
    fig, axs = plt.subplots(3, 2)
    fig.tight_layout(pad=1.0)

    plot_scatterplot(
        ax=axs[0][0],
        x_data=df.index.values,
        y_data=df["download_mbps"],
        mean=stats["download_mbps"]["mean"],
        std=stats["download_mbps"]["std"],
        title="Download Speed",
        y_label="Mbps",
    )
    plot_scatterplot(
        ax=axs[1][0],
        x_data=df.index.values,
        y_data=df["upload_mbps"],
        mean=stats["upload_mbps"]["mean"],
        std=stats["upload_mbps"]["std"],
        title="Upload Speed",
        y_label="Mbps",
    )
    plot_scatterplot(
        ax=axs[2][0],
        x_data=df.index.values,
        y_data=df["ping"],
        mean=stats["ping"]["mean"],
        std=stats["ping"]["std"],
        title="Ping",
        y_label="ms",
        x_label="Date",
    )

    bins = 10
    plot_histogram(
        ax=axs[0][1],
        data=df["download_mbps"],
        bins=bins,
        orientation="horizontal",
        mean=stats["download_mbps"]["mean"],
        std=stats["download_mbps"]["std"],
    )
    plot_histogram(
        ax=axs[1][1],
        data=df["upload_mbps"],
        bins=bins,
        orientation="horizontal",
        mean=stats["upload_mbps"]["mean"],
        std=stats["upload_mbps"]["std"],
    )
    plot_histogram(
        ax=axs[2][1],
        data=df["ping"],
        bins=bins,
        orientation="horizontal",
        mean=stats["ping"]["mean"],
        std=stats["ping"]["std"],
    )

    fig.autofmt_xdate()

    return fig


def plot_timeseries(df):
    fig, axs = plt.subplots(3, 1)
    fig.tight_layout(pad=1.0)

    axs[0].plot(df["timestamp"], df["download_mbps"], ".")
    axs[0].set_title("Download Speed")
    axs[0].set_ylabel("Mbps")

    axs[1].plot(df["timestamp"], df["upload_mbps"], ".")
    axs[1].set_title("Upload Speed")
    axs[1].set_ylabel("Mbps")

    axs[2].plot(df["timestamp"], df["ping"], ".")
    axs[2].set_title("Ping")
    axs[2].set_xlabel("Date")
    axs[2].set_ylabel("ms")

    return fig
