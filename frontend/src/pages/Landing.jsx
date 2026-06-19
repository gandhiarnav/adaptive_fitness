import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import logo from '../assets/logo.png';
import './Landing.css';

// Mifflin-St Jeor Calculator Constants
const ACTIVITY_MULTIPLIERS = {
  sedentary: 1.2,
  light: 1.375,
  moderate: 1.55,
  active: 1.725,
  very_active: 1.9,
};

const GOAL_ADJUSTMENTS = {
  lose_1_0: -1000,
  lose_0_5: -500,
  maintain: 0,
  gain_0_5: 500,
  gain_1_0: 1000,
};

export default function Landing() {
  // --- Calculator State ---
  const [gender, setGender] = useState('male');
  const [age, setAge] = useState(25);
  const [weight, setWeight] = useState(70); // in kg
  const [height, setHeight] = useState(175); // in cm
  const [activity, setActivity] = useState('moderate');
  const [goal, setGoal] = useState('maintain');

  const [results, setResults] = useState(null);

  // Run calculation when any state changes
  useEffect(() => {
    calculateMacros();
  }, [gender, age, weight, height, activity, goal]);

  const calculateMacros = () => {
    if (!age || !weight || !height) return;

    // 1. Calculate BMR using Mifflin-St Jeor
    let bmr = 0;
    if (gender === 'male') {
      bmr = 10 * weight + 6.25 * height - 5 * age + 5;
    } else {
      bmr = 10 * weight + 6.25 * height - 5 * age - 161;
    }

    // 2. Calculate TDEE
    const multiplier = ACTIVITY_MULTIPLIERS[activity];
    const tdee = Math.round(bmr * multiplier);

    // 3. Calculate Target Calories based on Goal
    const adjustment = GOAL_ADJUSTMENTS[goal];
    let targetCalories = tdee + adjustment;

    // Floor calories at safe minimums (1200 for female, 1500 for male)
    const minCalories = gender === 'female' ? 1200 : 1500;
    if (targetCalories < minCalories) {
      targetCalories = minCalories;
    }

    // 4. Calculate Macros
    // Protein: 2.0g per kg of body weight
    const proteinGrams = Math.round(weight * 2.0);
    const proteinCalories = proteinGrams * 4;

    // Fat: 25% of total calories
    const fatCalories = targetCalories * 0.25;
    const fatGrams = Math.round(fatCalories / 9);

    // Carbs: Remaining calories
    const carbCalories = Math.max(0, targetCalories - proteinCalories - fatCalories);
    const carbGrams = Math.round(carbCalories / 4);

    setResults({
      tdee,
      calories: targetCalories,
      protein: proteinGrams,
      fat: fatGrams,
      carbs: carbGrams,
    });
  };

  const handleScrollToCalculator = (e) => {
    e.preventDefault();
    const element = document.getElementById('macro-calculator');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="landing-container">
      {/* Background Blobs for Atmosphere */}
      <div className="glow-blob blob-top-left" />
      <div className="glow-blob blob-bottom-right" />
      <div className="glow-blob blob-center" />

      {/* --- HEADER --- */}
      <header className="landing-header">
        <div className="header-inner">
          <div className="logo-section">
            <img src={logo} alt="Adaptive Fitness Logo" className="nav-logo" />
            <span className="brand-name">Adaptive Fitness</span>
          </div>
          <nav className="nav-links">
            <a href="#features">Features</a>
            <a href="#macro-calculator" onClick={handleScrollToCalculator}>Calculator</a>
            <a href="#pricing">Why Us</a>
          </nav>
          <div className="auth-buttons">
            <Link to="/login" className="btn-signin">Sign In</Link>
            <Link to="/register" className="btn-getstarted">Get Started</Link>
          </div>
        </div>
      </header>

      {/* --- HERO SECTION --- */}
      <section className="hero-section">
        {/* Centered Heading Group */}
        <div className="hero-title-group">
          <span className="badge">AlphaZero's Adaptive Fitness</span>
          <h1 className="hero-title">
            Fitness that <span className="highlight-text">adapts</span> to you.
          </h1>
        </div>

        {/* Side-by-Side Content */}
        <div className="hero-split-content">
          <div className="hero-left-col">
            <p className="hero-description">
              Track meals instantly with natural language AI, log workouts, and let our dynamic macro engine update targets based on your actual metabolism and progress.
            </p>
            
            <div className="hero-ctas">
              <Link to="/register" className="cta-primary">Start Your Journey</Link>
              <a href="#macro-calculator" onClick={handleScrollToCalculator} className="cta-secondary">
                Calculate My Macros
              </a>
            </div>

            {/* Mockup Explanation */}
            <div className="mockup-explanation-card">
              <div className="explanation-text-block">
                <h4>Seamless Logging, Instant Feedback</h4>
                <p>
                  Describe your meals naturally—from complex home-cooked dishes to regional recipes. The system estimates calorie and protein counts instantly, updating your daily rings and macro bars in real time.
                </p>
              </div>
            </div>

            <div className="social-proof-mini">
              <p className="editorial-footnote">Join thousands of users tracking with artificial intelligence.</p>
            </div>
          </div>

          <div className="hero-right-col">
            {/* Hero Interactive App Mockup */}
            <div className="hero-mockup-container">
              <div className="mockup-frame">
                <div className="mockup-header">
                  <div className="dots">
                    <span className="dot" />
                    <span className="dot" />
                    <span className="dot" />
                  </div>
                  <div className="mockup-title">fit.alphazero.dev</div>
                </div>
                <div className="mockup-body">
                  <div className="mockup-nav">
                    <div className="mockup-nav-logo">
                      <div className="logo-bullet" />
                      Adaptive Fitness
                    </div>
                    <div className="mockup-avatar" />
                  </div>
                  <div className="mockup-main">
                    <div className="mockup-card progress-card">
                      <div className="mockup-ring">
                        <svg viewBox="0 0 100 100" className="mockup-ring-svg">
                          <circle cx="50" cy="50" r="40" className="bg" />
                          <circle cx="50" cy="50" r="40" className="fg" />
                        </svg>
                        <div className="mockup-ring-text">
                          <span className="val">1,640</span>
                          <span className="lbl">kcal left</span>
                        </div>
                      </div>
                      <div className="mockup-progress-stats">
                        <div className="stat-line">
                          <span>Target:</span>
                          <strong>2,200 kcal</strong>
                        </div>
                        <div className="stat-line">
                          <span>Consumed:</span>
                          <strong>560 kcal</strong>
                        </div>
                      </div>
                    </div>

                    <div className="mockup-card entry-card">
                      <span className="card-lbl">AI Food Log</span>
                      <div className="chat-bubble user">
                        "A bowl of chicken biryani and a glass of buttermilk"
                      </div>
                      <div className="chat-bubble ai">
                        <strong>Estimated:</strong> 520 kcal • 35g Protein
                      </div>
                    </div>

                    <div className="mockup-card macro-grid">
                      <div className="mini-bar">
                        <div className="bar-header"><span>Protein</span><strong>45g / 140g</strong></div>
                        <div className="bar-track"><div className="bar-fill" style={{ width: '32%', background: '#a78bfa' }} /></div>
                      </div>
                      <div className="mini-bar">
                        <div className="bar-header"><span>Carbs</span><strong>65g / 240g</strong></div>
                        <div className="bar-track"><div className="bar-fill" style={{ width: '27%', background: '#34d399' }} /></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* --- FEATURES SECTION --- */}
      <section id="features" className="features-section">
        <div className="section-header">
          <span className="section-tag">How It Works</span>
          <h2 className="section-title">Built for Smart Progression</h2>
          <p className="section-subtitle">
            Say goodbye to rigid calculators and tedious database searches. Adaptive Fitness leverages AI and dynamic math to keep your goals aligned with reality.
          </p>
        </div>

        <div className="features-grid">
          {/* Card 1: AI Estimator */}
          <div className="feature-card">
            <div className="feature-icon-wrapper purple">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2a10 10 0 0 1 10 10c0 5.523-4.477 10-10 10S2 17.523 2 12A10 10 0 0 1 12 2z" />
                <path d="M12 6v12M6 12h12" />
              </svg>
            </div>
            <h3>Natural Language AI Estimator</h3>
            <p>
              Log your food by describing it naturally. Our backend queries Google Gemini Flash to parse ingredients, estimate calories, and break down protein instantly.
            </p>
            <div className="feature-highlight">
              <em>"2 eggs, avocado toast, and black coffee" &rarr; 380 kcal</em>
            </div>
          </div>

          {/* Card 2: Adaptive Macros */}
          <div className="feature-card">
            <div className="feature-icon-wrapper green">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 3v18h18" />
                <path d="m18.7 8-5.1 5.2-2.8-2.7L7 14.3" />
              </svg>
            </div>
            <h3>Intelligent Macro Logic</h3>
            <p>
              Your TDEE isn't static. The platform dynamically recalculates your daily energy expenditure based on age, weight updates, activity changes, and goals.
            </p>
            <div className="feature-highlight">
              <em>Automatically offsets targets as your weight shifts.</em>
            </div>
          </div>

          {/* Card 3: Workout logs */}
          <div className="feature-card">
            <div className="feature-icon-wrapper yellow">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M6.5 6.5h11M6.5 12h11M6.5 17.5h11" />
                <rect x="3" y="3" width="18" height="18" rx="2" />
              </svg>
            </div>
            <h3>Clean Workout Journal</h3>
            <p>
              Log sets, reps, and weights for your weight training sessions. Filter historical workouts by date and track progressive overload smoothly.
            </p>
            <div className="feature-highlight">
              <em>No clutter, just rapid logging for serious lifters.</em>
            </div>
          </div>
        </div>
      </section>

      {/* --- INTERACTIVE CALCULATOR SECTION --- */}
      <section id="macro-calculator" className="calculator-section">
        <div className="calculator-wrapper glass-card">
          <div className="calculator-info">
            <span className="section-tag">Interactive Calculator</span>
            <h2>Calculate Your Macros Instantly</h2>
            <p>
              Get a preview of your custom daily calorie budget and target macros. Our widget uses the scientific Mifflin-St Jeor formula trusted by dieticians.
            </p>
            <p className="calculator-tip">
              <strong>Why register?</strong> Creating an account logs your profile parameters and adapts these macros as you log food and track workouts daily!
            </p>

            <div className="calculator-cta-box">
              <h3>Ready to lock in these targets?</h3>
              <Link to="/register" className="btn-calc-register">Create Free Account</Link>
            </div>
          </div>

          <div className="calculator-card">
            <div className="calc-inputs">
              {/* Gender */}
              <div className="calc-group">
                <label>Gender</label>
                <div className="calc-segmented">
                  <button
                    type="button"
                    className={gender === 'male' ? 'active' : ''}
                    onClick={() => setGender('male')}
                  >
                    Male
                  </button>
                  <button
                    type="button"
                    className={gender === 'female' ? 'active' : ''}
                    onClick={() => setGender('female')}
                  >
                    Female
                  </button>
                </div>
              </div>

              {/* Grid for parameters */}
              <div className="calc-grid">
                <div className="calc-group">
                  <label htmlFor="calc-weight">Weight (kg)</label>
                  <input
                    id="calc-weight"
                    type="number"
                    value={weight}
                    onChange={(e) => {
                      const val = e.target.value;
                      setWeight(val === '' ? '' : Math.max(1, parseInt(val) || 0));
                    }}
                  />
                </div>
                <div className="calc-group">
                  <label htmlFor="calc-height">Height (cm)</label>
                  <input
                    id="calc-height"
                    type="number"
                    value={height}
                    onChange={(e) => {
                      const val = e.target.value;
                      setHeight(val === '' ? '' : Math.max(1, parseInt(val) || 0));
                    }}
                  />
                </div>
                <div className="calc-group">
                  <label htmlFor="calc-age">Age (years)</label>
                  <input
                    id="calc-age"
                    type="number"
                    value={age}
                    onChange={(e) => {
                      const val = e.target.value;
                      setAge(val === '' ? '' : Math.max(1, parseInt(val) || 0));
                    }}
                  />
                </div>
              </div>

              {/* Activity Level */}
              <div className="calc-group">
                <label htmlFor="calc-activity">Activity Level</label>
                <select
                  id="calc-activity"
                  value={activity}
                  onChange={(e) => setActivity(e.target.value)}
                >
                  <option value="sedentary">Sedentary (Little/no exercise)</option>
                  <option value="light">Lightly Active (1-3 days/week)</option>
                  <option value="moderate">Moderately Active (3-5 days/week)</option>
                  <option value="active">Very Active (6-7 days/week)</option>
                  <option value="very_active">Athlete / Physical Job</option>
                </select>
              </div>

              {/* Fitness Goal */}
              <div className="calc-group">
                <label htmlFor="calc-goal">Fitness Goal</label>
                <select
                  id="calc-goal"
                  value={goal}
                  onChange={(e) => setGoal(e.target.value)}
                >
                  <option value="lose_1_0">Extreme Weight Loss (-1.0 kg/week)</option>
                  <option value="lose_0_5">Moderate Weight Loss (-0.5 kg/week)</option>
                  <option value="maintain">Maintain Current Weight</option>
                  <option value="gain_0_5">Slow Muscle Gain (+0.5 kg/week)</option>
                  <option value="gain_1_0">Fast Weight Gain (+1.0 kg/week)</option>
                </select>
              </div>
            </div>

            {/* Results Display */}
            {results && (
              <div className="calc-results animate-fade-in">
                <div className="results-calories">
                  <span className="lbl">Daily Calorie Target</span>
                  <span className="val">{results.calories.toLocaleString()} kcal</span>
                  <span className="sub">Estimated TDEE: {results.tdee.toLocaleString()} kcal</span>
                </div>

                <div className="results-macros">
                  {/* Protein */}
                  <div className="macro-result-item">
                    <div className="macro-header">
                      <span className="macro-dot protein" />
                      <span>Protein</span>
                      <strong>{results.protein}g</strong>
                    </div>
                    <div className="macro-track">
                      <div className="macro-fill protein" style={{ width: `${Math.min(100, (results.protein / 200) * 100)}%` }} />
                    </div>
                  </div>

                  {/* Carbs */}
                  <div className="macro-result-item">
                    <div className="macro-header">
                      <span className="macro-dot carbs" />
                      <span>Carbohydrates</span>
                      <strong>{results.carbs}g</strong>
                    </div>
                    <div className="macro-track">
                      <div className="macro-fill carbs" style={{ width: `${Math.min(100, (results.carbs / 350) * 100)}%` }} />
                    </div>
                  </div>

                  {/* Fat */}
                  <div className="macro-result-item">
                    <div className="macro-header">
                      <span className="macro-dot fat" />
                      <span>Dietary Fat</span>
                      <strong>{results.fat}g</strong>
                    </div>
                    <div className="macro-track">
                      <div className="macro-fill fat" style={{ width: `${Math.min(100, (results.fat / 100) * 100)}%` }} />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* --- CALL TO ACTION --- */}
      <section className="cta-banner-section">
        <div className="cta-banner-inner">
          <h2>Stop Guessing. Start Tracking Smarter.</h2>
          <p>Get instant estimations, track workouts, and adapt your targets in real time.</p>
          <Link to="/register" className="cta-banner-btn">Create Your Free Account Now</Link>
        </div>
      </section>

      {/* --- FOOTER --- */}
      <footer className="landing-footer">
        <div className="footer-inner">
          <p className="copyright">&copy; {new Date().getFullYear()} Adaptive Fitness. All rights reserved.</p>
          <div className="footer-links">
            <Link to="/login">Sign In</Link>
            <Link to="/register">Sign Up</Link>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer">Source Code</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
