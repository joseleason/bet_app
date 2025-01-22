import streamlit as st


def american_to_net_odds(american_ml: float) -> float:
    """
    Convert an American moneyline to 'net odds' (the profit per $1 stake).

    For example:
      - If ML = +150, net odds = 1.50 (profit is $1.50 for every $1 bet).
      - If ML = -130, net odds = 0.769... (profit is $0.769 for every $1 bet).
    """
    if american_ml > 0:
        return american_ml / 100.0
    else:
        return 100.0 / abs(american_ml)


def kelly_fraction(prob: float, net_odds: float) -> float:
    """
    Kelly fraction = ((b + 1)*p - 1) / b
      where p = probability of winning, b = net_odds.
    Returns 0 if fraction is negative (i.e., no bet).
    """
    # b = net_odds
    fraction = prob - (1 - prob) / net_odds
    return max(0.0, fraction)


def recommended_bet_size(prob: float, american_ml: float, fraction_kelly: float,
                         morning_bank: float, max_bet_fraction: float) -> float:
    """
    1) Convert American ML to net odds
    2) Compute Kelly fraction
    3) Multiply by 'fraction_kelly' (user-chosen fraction of full Kelly)
    4) Multiply by 'morning_bank'
    5) Cap by max_bet_fraction * morning_bank
    6) Return final recommended stake (>= 0).
    """
    b = american_to_net_odds(american_ml)
    kf = kelly_fraction(prob, b)  # raw Kelly fraction
    raw_bet = fraction_kelly * kf * morning_bank
    cap = max_bet_fraction * morning_bank
    return min(raw_bet, cap), kf


def main():
    st.title("Kelly Criterion Bet Sizing (Home/Away)")

    st.write("Enter the relevant information below to calculate recommended bet sizes.")

    # User inputs
    home_ml = st.number_input("Home American Moneyline", value=-110.0, step=5.0, format="%.2f")
    away_ml = st.number_input("Away American Moneyline", value=-110.0, step=5.0, format="%.2f")
    fraction_k = st.number_input("Fraction of Kelly Criterion (e.g. 0.5 for half Kelly)",
                                 value=1.0, min_value=0.0, step=0.05, format="%.2f")
    model_prob_home = st.number_input("Model Probability of Home Win",
                                      value=0.50, min_value=0.0, max_value=1.0, step=0.01, format="%.2f")
    morning_bank = st.number_input("Morning Bank", value=2000.0, step=50.0, format="%.2f")
    max_bet_frac = st.number_input("Max Bet Fraction (of bank)", value=0.1, min_value=0.0, step=0.05, format="%.2f")

    if st.button("Calculate Bet Sizes"):
        # Probability for away is just 1 - model_prob_home
        p_away = 1.0 - model_prob_home

        home_bet, home_kf = recommended_bet_size(
            prob=model_prob_home,
            american_ml=home_ml,
            fraction_kelly=fraction_k,
            morning_bank=morning_bank,
            max_bet_fraction=max_bet_frac
        )

        away_bet, away_kf = recommended_bet_size(
            prob=p_away,
            american_ml=away_ml,
            fraction_kelly=fraction_k,
            morning_bank=morning_bank,
            max_bet_fraction=max_bet_frac
        )

        st.subheader("Results")
        st.write(f"**Recommended Home Bet**:  \${home_bet:,.2f}")
        st.write(f"**Recommended Away Bet**:  \${away_bet:,.2f}")

        st.subheader("Additional information")
        st.write(f"**Raw Kelly Home Bet**:  {home_kf:,.2f}")
        st.write(f"**Raw Kelly Away Bet**:  {away_kf:,.2f}")

        # If both Kelly fractions are positive, user might only want one side.
        # Typically you pick the side that has the higher EV, but we leave that decision to the user.


if __name__ == "__main__":
    main()