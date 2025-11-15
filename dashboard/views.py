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

@login_required(login_url='login')
def dashboard_home(request):
    if request.method == 'POST':
        form = FitnessDataForm(request.POST)
        if form.is_valid():
            fitness_data = form.save(commit=False)
            fitness_data.user = request.user
            fitness_data.save()
            return redirect('dashboard')
    else:
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

    # Generate weight & BMI plot
    dates = [record.date for record in user_data]
    weights = [record.weight for record in user_data]
    bmis = [record.bmi for record in user_data]

    plt.figure(figsize=(6, 4))
    plt.plot(dates, bmis, marker='o', label='Recorded BMI')

    # --- Add trendline (only if enough data) ---
    if len(bmis) >= 3:
        x = np.arange(1, len(bmis) + 1)
        bmi_slope, bmi_intercept, *_ = stats.linregress(x, bmis)

        # Predict for current + next point
        x_extended = np.append(x, len(bmis) + 1)
        predicted_bmis = bmi_intercept + bmi_slope * x_extended

        # Plot trendline
        next_week_date = dates[-1] + np.timedelta64(7, 'D') if dates else np.datetime64('today')
        plt.plot(dates + [next_week_date], predicted_bmis, linestyle='--', color='orange', label='Predicted Trend')

    plt.title('BMI Trend Over Time')
    plt.xlabel('Date')
    plt.xticks(rotation=45)
    plt.gcf().autofmt_xdate()
    plt.ylabel('BMI')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    # Save plot to a string buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    buf.close()
    plot_data = urllib.parse.quote(string)
    plt.close()

    # --- Weight Trend Prediction ---
    if user_data.count() >= 3:
        weights = np.array([record.weight for record in user_data])
        x = np.arange(1, len(weights) + 1)

        # Linear regression for weight
        weight_slope, weight_intercept, *_ = stats.linregress(x, weights)

        next_week_weight = round(weight_intercept + weight_slope * (len(weights) + 1), 2)
    else:
        next_week_weight = None

    # --- Weight Trend Chart ---
    plt.figure(figsize=(6, 4))
    plt.plot(dates, weights, marker='o', label='Recorded Weight')

    if len(weights) >= 3:
        x_extended = np.append(x, len(weights) + 1)
        predicted_weights = weight_intercept + weight_slope * x_extended
        next_week_date = dates[-1] + np.timedelta64(7, 'D') if dates else np.datetime64('today')
        plt.plot(dates + [next_week_date], predicted_weights, linestyle='--', color='green', label='Predicted Trend')

    plt.title('Weight Trend Over Time')
    plt.xlabel('Date')
    plt.xticks(rotation=45)
    plt.gcf().autofmt_xdate()
    plt.ylabel('Weight (kg)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    # Convert to base64 to display in template
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    weight_chart = base64.b64encode(image_png).decode('utf-8')
    plt.close()

    bmi_chart_light = generate_chart(dates, bmis, "BMI Over Time", line_color='blue', dark_mode=False)
    bmi_chart_dark = generate_chart(dates, bmis, "BMI Over Time", line_color='blue', dark_mode=True)
    weight_chart_light = generate_chart(dates, weights, "Weight Over Time", line_color='green', dark_mode=False)
    weight_chart_dark = generate_chart(dates, weights, "Weight Over Time", line_color='green', dark_mode=True)

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

def generate_chart(x_labels, y_data, title, line_color, dark_mode=False):
    plt.figure(figsize=(6, 4))

    # Background and grid for dark mode
    if dark_mode:
        plt.style.use('dark_background')
        bg_color = '#1e1e1e'
        grid_color = '#555555'
    else:
        plt.style.use('default')
        bg_color = 'white'
        grid_color = '#cccccc'

    plt.plot(x_labels, y_data, marker='o', color=line_color, label='Recorded')

    # Trendline if enough data
    if len(y_data) >= 3:
        x = np.arange(1, len(y_data) + 1)
        slope, intercept, *_ = stats.linregress(x, y_data)
        x_extended = np.append(x, len(y_data) + 1)
        predicted = intercept + slope * x_extended
        if len(x_labels) > 0:
            next_week_date = np.datetime64(x_labels[-1]) + np.timedelta64(7, 'D')
        else:
            next_week_date = np.datetime64('today') + np.timedelta64(7, 'D')

        plt.plot(list(x_labels) + [next_week_date], predicted,
                 linestyle='--', color='orange' if not dark_mode else 'violet',
                 label='Predicted Trend')

    plt.title(title, color='#e0d9ff' if dark_mode else 'black')
    plt.xlabel('Date', color='#e0d9ff' if dark_mode else 'black')
    plt.xticks(rotation=45)
    plt.gcf().autofmt_xdate()
    plt.ylabel(title.split()[0], color='#e0d9ff' if dark_mode else 'black')
    plt.grid(True, color=grid_color, linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor=bg_color)
    buf.seek(0)
    img_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    return img_data

def reset_data(request):
    # Delete all fitness records for the current user
    FitnessData.objects.filter(user=request.user).delete()

    messages.success(request, "All your fitness data has been reset successfully.")
    return redirect('dashboard')