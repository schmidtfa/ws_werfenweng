#Just a bunch of functions used for plotting

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import arviz as az


#Vizualize predictions:
def plot_linear_regression(df, fitted, x_key, y_key, random_factor=None, add_hdi=True):

    '''This function can be used to visualize the results of a bayesian linear regression.
        
        df: Pandas DataFrame of the data used to build the model
        fitted: InferenceData object of the fitted model
        x_key: String referring to the x-axis label
        y_key: String referring to the y-axis label
        random_factor:  if this is a string use it to get information for plotting
        
        Note: Requires model prediction to be run first to get y mean
    '''
    
    Intercept = fitted.posterior.Intercept.values.mean()
    Slope = fitted.posterior[x_key].values.mean()
    x_range = np.linspace(df[x_key].min(), df[x_key].max(), fitted.posterior.dims['draw'])
    regression_line = Intercept + Slope * x_range

    g = sns.scatterplot(x=x_key, y=y_key, data=df, color='#0f4c81', alpha=0.5)
    plt.plot(x_range, regression_line, color='#333333', linewidth=3)
    
    if add_hdi == True:
        if random_factor == None:
            hdi2plot = fitted.posterior[f"{y_key}_mean"]
            az.plot_hdi(x=df[x_key], y=hdi2plot, color='#777777')
        else:
            #annoying & tedious but safe
            reaction_mean = fitted.posterior[f"{y_key}_mean"].stack(samples=("draw", "chain")).values
            hdi_list = []

            for _, subject in enumerate(df[random_factor].unique()):
                idx = df.index[df[random_factor] == subject].tolist()
                hdi_list.append(reaction_mean[idx].T)
            
            hdi2plot = np.array(hdi_list)
            az.plot_hdi(x=df[x_key].unique(), y=hdi2plot, color='#777777', hdi_prob=0.68)
        
    return g



def plot_individual_sleep_data(sleepstudy, fitted):

    '''
    This function is 100% tailored to the sleep dataset and 99% copied from a bambi tutorial.
    This will only work for the sleepstudy data!
    '''

    fig, axes = plt.subplots(2, 9, figsize=(16, 7.5), sharey=True, sharex=True, dpi=300)
    fig.subplots_adjust(left=0.075, right=0.975, bottom=0.075, top=0.925, wspace=0.03)

    axes_flat = axes.ravel()

    for i, subject in enumerate(sleepstudy["Subject"].unique()):
        ax = axes_flat[i]
        idx = sleepstudy.index[sleepstudy["Subject"] == subject].tolist()
        days = sleepstudy.loc[idx, "Days"].values
        reaction = sleepstudy.loc[idx, "Reaction"].values

        # Plot observed data points
        ax.scatter(days, reaction, color="C0", ec="black", alpha=0.7)

        # Add a title
        ax.set_title(f"Subject: {subject}", fontsize=14)

    ax.xaxis.set_ticks([0, 2, 4, 6, 8])
    fig.text(0.5, 0.02, "Days", fontsize=14)
    fig.text(0.03, 0.5, "Reaction time (ms)", rotation=90, fontsize=14, va="center")
    
    axes_flat = axes.ravel()

    # Take the posterior of the mean reaction time
    reaction_mean = fitted.posterior["Reaction_mean"].stack(samples=("draw", "chain")).values

    for i, subject in enumerate(sleepstudy["Subject"].unique()):
        ax = axes_flat[i]
        idx = sleepstudy.index[sleepstudy["Subject"]== subject].tolist()
        days = sleepstudy.loc[idx, "Days"].values

        # Plot highest density interval / credibility interval
        az.plot_hdi(days, reaction_mean[idx].T[np.newaxis], color="C0", ax=ax)

        # Plot mean regression line
        ax.plot(days, reaction_mean[idx].mean(axis=1), color="C0")

    return axes