from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import FitnessDataForm
from .models import FitnessData
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')  # needed for Django to generate images without GUI
import matplotlib.pyplot as plt
import io
import urllib, base64
from utils.matplotlib_theme import apply_shadcn_light_theme, apply_shadcn_dark_theme
from datetime import datetime, date, timedelta  # added import

@login_required(login_url='login')
def dashboard_home(request):
    form = FitnessDataForm()

    # Get all user's fitness records
    user_data = FitnessData.objects.filter(user=request.user).order_by('-date')

    # Extract weight and height for calculations
    weights = np.array([record.weight for record in user_data])
    heights = np.array([record.height for record in user_data])
    steps = np.array([record.steps for record in user_data])
    calories = np.array([record.calories_burned for record in user_data])

    # Calculate average steps and calories
    steps = np.array([record.steps for record in user_data])
    calories = np.array([record.calories_burned for record in user_data])

    avg_steps = int(np.mean(steps)) if len(steps) > 0 else 0
    avg_calories = int(np.mean(calories)) if len(calories) > 0 else 0

    # --- PREDICTION SECTION ---
    if user_data.count() >= 3:  # need at least 3 records for a trend
        weights = np.array([record.weight for record in user_data])
        bmis = np.array([record.bmi for record in user_data])
        steps = np.array([record.steps for record in user_data])

        # Use time indices as x-values (1, 2, 3, ...)
        x = np.arange(1, len(user_data) + 1)

        # Predict next BMI and steps using linear regression
        bmi_slope, bmi_intercept, *_ = stats.linregress(x, bmis)
        step_slope, step_intercept, *_ = stats.linregress(x, steps)

        next_week_bmi = round(bmi_intercept + bmi_slope * (len(user_data) + 1), 2)
        next_week_steps = round(step_intercept + step_slope * (len(user_data) + 1))

        # Motivation message
        if step_slope > 0:
            motivation = f"🔥 Great work! You’re on track to increase your step count by about {round(step_slope, 1)} steps/day. Keep that momentum!"
        elif bmi_slope < 0:
            motivation = "💪 Your BMI trend is improving — keep maintaining that healthy balance!"
        else:
            motivation = "🌟 You’re maintaining steady progress. Try adding small challenges next week!"
    else:
        next_week_bmi = None
        next_week_steps = None
        motivation = "Add more data to see your progress predictions!"

    # --- Prepare raw lists used by charts ---
    dates = [record.date for record in user_data]
    weights = [record.weight for record in user_data]
    bmis = [record.bmi for record in user_data]

    # --- Ensure next_week_weight is calculated (used in context) ---
    if len(weights) >= 3:
        x_w = np.arange(1, len(weights) + 1)
        weight_slope, weight_intercept, *_ = stats.linregress(x_w, weights)
        next_week_weight = round(weight_intercept + weight_slope * (len(weights) + 1), 2)
    else:
        next_week_weight = None

    # Generate BMI and Weight charts (light + dark)
    bmi_chart_light = generate_chart(dates, bmis, title="BMI Trend Over Time", line_color='#0078d4', dark_mode=False)
    bmi_chart_dark = generate_chart(dates, bmis, title="BMI Trend Over Time", line_color='#6e14b4', dark_mode=True)

    weight_chart_light = generate_chart(dates, weights, title="Weight Trend Over Time", line_color='#0078d4', dark_mode=False)
    weight_chart_dark = generate_chart(dates, weights, title="Weight Trend Over Time", line_color='#6e14b4', dark_mode=True)

    # Provide simple flags for templates (used to decide whether to show charts)
    plot_data = len(bmis) > 0
    weight_chart = len(weights) > 0

    context = {
        'form': form,
        'user_data': user_data,
        'avg_steps': avg_steps,
        'avg_calories': avg_calories,
        'plot_data': plot_data,
        'weight_chart': weight_chart,
        "next_week_bmi": next_week_bmi,
        "next_week_weight": next_week_weight,
        "next_week_steps": next_week_steps,
        "motivation": motivation,
        "bmi_chart_light": bmi_chart_light,
        "bmi_chart_dark": bmi_chart_dark,
        "weight_chart_light": weight_chart_light,
        "weight_chart_dark": weight_chart_dark,
    }

    return render(request, 'dashboard/home.html', context)

@login_required(login_url='login')
def add_record(request):
    """Handle add fitness data on separate page."""
    if request.method == 'POST':
        form = FitnessDataForm(request.POST)
        if form.is_valid():
            fitness_data = form.save(commit=False)
            fitness_data.user = request.user
            fitness_data.save()
            messages.success(request, "Record added successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = FitnessDataForm()

    return render(request, 'dashboard/add_record.html', {'form': form})

def generate_chart(x_labels, y_data, title, line_color='#0078d4', dark_mode=False):
    # Apply shadcn theme for consistent look
    if dark_mode:
        apply_shadcn_dark_theme()
    else:
        apply_shadcn_light_theme()

    fig, ax = plt.subplots(figsize=(10, 5))  # consistent size for all charts
    ax.plot(x_labels, y_data, marker='o', color=line_color, linewidth=2.5, label='Recorded')

    # Trendline if enough data
    if len(y_data) >= 3:
        x = np.arange(1, len(y_data) + 1)
        slope, intercept, *_ = stats.linregress(x, y_data)
        x_extended = np.append(x, len(y_data) + 1)
        predicted = intercept + slope * x_extended

        # compute next_week_date robustly for numpy datetime64 or python date/datetime
        def add_7_days(lbl):
            try:
                if isinstance(lbl, np.datetime64):
                    # convert numpy datetime64 to python datetime
                    py_dt = lbl.astype('datetime64[s]').astype('O')
                    return py_dt + timedelta(days=7)
                if isinstance(lbl, (datetime, date)):
                    return lbl + timedelta(days=7)
                # fallback: try parsing ISO-like stringtring
                return datetime.fromisoformat(str(lbl)) + timedelta(days=7)
            except Exception:
                return datetime.now() + timedelta(days=7)

        if len(x_labels) > 0:
            next_week_date = add_7_days(x_labels[-1])
        else:
            next_week_date = datetime.now() + timedelta(days=7)

        ax.plot(list(x_labels) + [next_week_date], predicted,
                linestyle='--', color='orange' if not dark_mode else 'violet',
                label='Predicted Trend')

    # Titles and labels (colors adapt to dark mode via theme)
    text_color = '#e0d9ff' if dark_mode else '#111111'
    ax.set_title(title, fontsize=14, fontweight='bold', color=text_color)
    ax.set_xlabel('Date', color=text_color)
    ax.set_ylabel(title.split()[0], color=text_color)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(frameon=False)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png', facecolor=fig.get_facecolor())
    buf.seek(0)
    img_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return img_data

def reset_data(request):
    # Delete all fitness records for the current user
    FitnessData.objects.filter(user=request.user).delete()

    messages.success(request, "All your fitness data has been reset successfully.")
    return redirect('dashboard')