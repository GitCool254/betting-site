from flask import Flask, request, jsonify, render_template
import math

app = Flask(__name__)

def poisson_prob(lambda_goals, k):
    """Calculate Poisson probability P(k) = (λ^k * e^-λ) / k!"""
    return (lambda_goals ** k) * math.exp(-lambda_goals) / math.factorial(k)

@app.route('/')
def index():
    # Serve the frontend HTML page
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()

    # Extract inputs (convert to float)
    home_avg_scored = float(data['homeAttack'])      # raw avg goals scored
    home_avg_conceded = float(data['homeDefence'])   # raw avg goals conceded
    home_form = float(data['homeForm'])
    home_league_avg = float(data['homeLeagueAvg'])   # NEW: Home League Average

    away_avg_scored = float(data['awayAttack'])      # raw avg goals scored
    away_avg_conceded = float(data['awayDefence'])   # raw avg goals conceded
    away_form = float(data['awayForm'])
    away_league_avg = float(data['awayLeagueAvg'])   # NEW: Away League Average

    # --- Compute strengths using respective league averages ---
    home_attack_strength = home_avg_scored / home_league_avg
    home_defence_strength = home_avg_conceded / home_league_avg
    away_attack_strength = away_avg_scored / away_league_avg
    away_defence_strength = away_avg_conceded / away_league_avg

    # Step 1: Expected goals (formula unchanged, using corresponding league averages)
    home_xg = home_attack_strength * away_defence_strength * home_league_avg * home_form
    away_xg = away_attack_strength * home_defence_strength * away_league_avg * away_form

    # Step 2: Poisson probabilities for 0..4 goals
    max_goals = 4
    home_probs = [poisson_prob(home_xg, g) for g in range(max_goals + 1)]
    away_probs = [poisson_prob(away_xg, g) for g in range(max_goals + 1)]

    # Step 3: Multiply for all scorelines
    results = []
    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            prob = home_probs[h] * away_probs[a] * 100  # as percentage
            scoreline = f"Home ({h}) : Away ({a})"
            results.append({
                "scoreline": scoreline,
                "probability": round(prob, 2)
            })

    # Step 4: Sort descending by probability
    results.sort(key=lambda x: x['probability'], reverse=True)

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
