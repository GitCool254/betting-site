from flask import Flask, request, jsonify, render_template
import math

app = Flask(__name__)

def poisson_prob(lambda_goals, k):
    """Calculate Poisson probability P(k) = (λ^k * e^-λ) / k!"""
    return (lambda_goals ** k) * math.exp(-lambda_goals) / math.factorial(k)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()

    # Extract inputs
    home_avg_scored = float(data['homeAttack'])
    home_avg_conceded = float(data['homeDefence'])
    home_form = float(data['homeForm'])
    home_league_avg = float(data['homeLeagueAvg'])

    away_avg_scored = float(data['awayAttack'])
    away_avg_conceded = float(data['awayDefence'])
    away_form = float(data['awayForm'])
    away_league_avg = float(data['awayLeagueAvg'])

    # Compute strengths
    home_attack_strength = home_avg_scored / home_league_avg
    home_defence_strength = home_avg_conceded / home_league_avg
    away_attack_strength = away_avg_scored / away_league_avg
    away_defence_strength = away_avg_conceded / away_league_avg

    # Expected goals
    home_xg = home_attack_strength * away_defence_strength * home_league_avg * home_form
    away_xg = away_attack_strength * home_defence_strength * away_league_avg * away_form

    # Use a larger max_goals for better accuracy
    max_goals = 10
    home_probs = [poisson_prob(home_xg, g) for g in range(max_goals + 1)]
    away_probs = [poisson_prob(away_xg, g) for g in range(max_goals + 1)]

    # Initialise accumulators
    home_win_prob = 0.0
    away_win_prob = 0.0
    draw_prob = 0.0
    btts_prob = 0.0
    under_05 = 0.0
    under_15 = 0.0
    under_25 = 0.0
    under_35 = 0.0
    over_15 = 0.0
    over_25 = 0.0
    over_35 = 0.0

    results = []  # for scoreline probabilities

    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            prob = home_probs[h] * away_probs[a]
            prob_percent = prob * 100
            scoreline = f"Home ({h}) : Away ({a})"
            results.append({
                "scoreline": scoreline,
                "probability": round(prob_percent, 2)
            })

            # Update aggregates
            if h > a:
                home_win_prob += prob
            elif h < a:
                away_win_prob += prob
            else:  # h == a
                draw_prob += prob

            if h >= 1 and a >= 1:
                btts_prob += prob

            total = h + a
            # Under thresholds
            if total <= 0:     # under 0.5
                under_05 += prob
            if total <= 1:     # under 1.5
                under_15 += prob
            if total <= 2:     # under 2.5
                under_25 += prob
            if total <= 3:     # under 3.5
                under_35 += prob
            # Over thresholds
            if total >= 2:     # over 1.5
                over_15 += prob
            if total >= 3:     # over 2.5
                over_25 += prob
            if total >= 4:     # over 3.5
                over_35 += prob

    # Convert aggregates to percentages
    home_win_prob *= 100
    away_win_prob *= 100
    draw_prob *= 100
    btts_prob *= 100
    under_05 *= 100
    under_15 *= 100
    under_25 *= 100
    under_35 *= 100
    over_15 *= 100
    over_25 *= 100
    over_35 *= 100

    # Sort scoreline results descending
    results.sort(key=lambda x: x['probability'], reverse=True)

    response = {
        "results": results,
        "home_win": round(home_win_prob, 2),
        "away_win": round(away_win_prob, 2),
        "draw": round(draw_prob, 2),
        "btts": round(btts_prob, 2),
        "under_05": round(under_05, 2),
        "under_15": round(under_15, 2),
        "under_25": round(under_25, 2),
        "under_35": round(under_35, 2),
        "over_15": round(over_15, 2),
        "over_25": round(over_25, 2),
        "over_35": round(over_35, 2),
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
