import streamlit as st
from datetime import datetime
import io

st.set_page_config(
    page_title="🐎 Universal Horse Racing Predictor",
    page_icon="🐎",
    layout="wide"
)

class UniversalHorseRacingPredictor:
    def __init__(self):
        self.weights = {
            'speed_figure': 0.30,      # Most important
            'recent_form': 0.25,       # Recent performance
            'class_level': 0.15,       # Competition level
            'post_position': 0.10,     # Starting gate
            'jockey_skill': 0.10,      # Jockey ability
            'trainer_stats': 0.08,     # Trainer stats
            'distance_fitness': 0.02   # Distance suitability
        }
        
        # Universal post position weights (works for any field size)
        self.post_weights = self.generate_post_weights()

    def generate_post_weights(self, max_posts=20):
        """Generate post position weights for any field size"""
        weights = {}
        for total_posts in range(4, max_posts + 1):
            post_weights = {}
            for post in range(1, total_posts + 1):
                if post <= 3:
                    post_weights[post] = 1.0 - (post - 1) * 0.02  # Inside posts advantage
                elif post <= 8:
                    post_weights[post] = 1.0  # Neutral posts
                else:
                    post_weights[post] = 1.0 - (post - 8) * 0.03  # Outside posts penalty
            weights[total_posts] = post_weights
        return weights

    def calculate_universal_score(self, horse_data):
        """Universal scoring algorithm that works for any racing format"""
        
        # Speed Score (universal)
        speed_base = horse_data.get('speed_rating', 70)
        speed_bonus = 0
        
        # Recent Form Score (universal)
        recent_form = horse_data.get('recent_finishes', [5, 5, 5])
        form_score = 0
        if recent_form:
            total_races = len(recent_form)
            for i, finish in enumerate(reversed(recent_form)):
                weight = (i + 1) / total_races
                position_score = max(0, (10 - finish) / 10)
                form_score += position_score * weight
            form_score = form_score / sum([(i+1)/total_races for i in range(total_races)]) if total_races > 0 else 0.5
        
        # Post Position Score (universal)
        post = horse_data.get('post_position', 5)
        field_size = horse_data.get('field_size', 10)
        post_score = self.post_weights.get(field_size, {}).get(post, 0.95)
        
        # Class Score (universal)
        class_bonus = 1.0
        if horse_data.get('race_class') and horse_data.get('horse_class'):
            if horse_data['horse_class'] > horse_data['race_class']:
                class_bonus = 1.15  # Dropping in class
            elif horse_data['horse_class'] < horse_data['race_class']:
                class_bonus = 0.85  # Moving up in class
        
        # Calculate universal score
        total_score = (
            speed_base * self.weights['speed_figure'] +
            form_score * 100 * self.weights['recent_form'] +
            post_score * 100 * self.weights['post_position'] +
            class_bonus * 100 * self.weights['class_level']
        )
        
        return total_score

    def predict_universal_race(self, horses_data):
        """Universal race prediction for any format"""
        results = []
        
        for horse in horses_data:
            score = self.calculate_universal_score(horse)
            
            results.append({
                'Horse': horse.get('name', 'Unknown'),
                'Score': round(score, 2),
                'Win_Probability': round(max(0, score - 70), 1),
                'Post_Position': horse.get('post_position', '?'),
                'Weight': horse.get('weight', '?'),
                'Jockey': horse.get('jockey', '?'),
                'Trainer': horse.get('trainer', '?'),
                'Speed_Rating': horse.get('speed_rating', '?'),
                'Recent_Form': horse.get('recent_finishes', '?'),
                'Analysis': self.generate_universal_analysis(horse)
            })
        
        # Sort by score
        results.sort(key=lambda x: x['Score'], reverse=True)
        
        # Normalize probabilities
        total_prob = sum([r['Win_Probability'] for r in results])
        if total_prob > 0:
            for result in results:
                result['Win_Probability'] = (result['Win_Probability'] / total_prob * 100).round(1)
        
        return results

    def generate_universal_analysis(self, horse_data):
        """Generate analysis that works for any racing format"""
        analysis = []
        
        # Post position analysis
        post = horse_data.get('post_position', 5)
        field_size = horse_data.get('field_size', 10)
        if post <= 3:
            analysis.append("🎯 Good inside post")
        elif post >= field_size - 2:
            analysis.append("⚠️ Wide post challenge")
        
        # Recent form analysis
        recent = horse_data.get('recent_finishes', [])
        if recent:
            avg_finish = sum(recent) / len(recent)
            if avg_finish <= 3:
                analysis.append("🔥 Strong recent form")
            elif avg_finish <= 6:
                analysis.append("📊 Consistent performer")
            else:
                analysis.append("📉 Needs improvement")
        
        # Weight analysis (if available)
        weight = horse_data.get('weight', 0)
        if weight > 0:
            if weight < 54:
                analysis.append("⚖️ Light weight advantage")
            elif weight > 57:
                analysis.append("🏋️ Heavy weight to carry")
        
        return " | ".join(analysis) if analysis else "📊 Standard contender"

def extract_universal_racing_data(text_content):
    """Universal racing data extractor - works with ANY format"""
    horses = []
    lines = text_content.strip().split('\n')
    
    # Multiple extraction strategies
    strategies = [
        # Strategy 1: Post Position + Name Pattern
        r'(\d+)\s+([A-Z][A-Z\s]+?)(?:\s+\d+|\s+[A-Z]|\s*$)',
        
        # Strategy 2: Name + Numbers Pattern  
        r'([A-Z][A-Za-z\s\-\']+?)\s+(\d+(?:\.\d+)?)\s+([\d\s;,\.]+)',
        
        # Strategy 3: Table-like format
        r'(\d+)\s+([A-Za-z\s\-\']+)\s+(\d+(?:\.\d+)?)\s+([\d\s;,\.]+)',
        
        # Strategy 4: Flexible name capture
        r'([A-Z][A-Za-z\s\-\']{3,25}?)\s+(\d+(?:\.\d+)?)'
    ]
    
    for strategy in strategies:
        matches = []
        for line in lines:
            match = re.findall(strategy, line, re.IGNORECASE)
            if match:
                matches.extend(match)
        
        if len(matches) >= 2:  # Found at least 2 horses
            for match in matches[:20]:  # Limit to 20 horses max
                try:
                    if len(match) >= 2:
                        horse_data = {
                            'name': match[1].strip() if len(match) > 1 else match[0].strip(),
                            'post_position': int(match[0]) if len(match) > 1 and match[0].isdigit() else len(horses) + 1,
                            'weight': 55,  # Default weight
                            'recent_finishes': [],
                            'jockey_win_percentage': 0.12,
                            'trainer_win_percentage': 0.15,
                            'field_size': len(matches),
                            'race_distance': 8.0,
                            'track_condition': 'fast',
                            'speed_rating': 75,
                            'race_class': 'allowance',
                            'horse_class': 'allowance'
                        }
                        
                        # Extract numbers as recent form
                        numbers_found = []
                        for part in match[2:] if len(match) > 2 else []:
                            nums = re.findall(r'(\d+(?:\.\d+)?)', str(part))
                            for num in nums:
                                try:
                                    n = float(num)
                                    if 1 <= n <= 20:  # Reasonable race position
                                        numbers_found.append(int(n))
                                except:
                                    continue
                        
                        horse_data['recent_finishes'] = numbers_found[:5] if numbers_found else [5, 5, 5]
                        
                        # Extract weight if found
                        weight_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(?:kg|KG|K🇬|kg)', line, re.IGNORECASE)
                        if weight_matches:
                            horse_data['weight'] = float(weight_matches[0])
                        
                        horses.append(horse_data)
                except:
                    continue
            break
    
    # Fallback: Simple line-by-line extraction
    if not horses:
        for i, line in enumerate(lines):
            # Look for lines with both letters and numbers
            if re.search(r'[A-Za-z]', line) and re.search(r'\d', line):
                words = re.findall(r'[A-Za-z]+', line)
                numbers = re.findall(r'\d+(?:\.\d+)?', line)
                
                if len(words) >= 1 and len(numbers) >= 2:
                    horse_data = {
                        'name': ' '.join(words[:3]),  # First 1-3 words as name
                        'post_position': i + 1,
                        'weight': 55,
                        'recent_finishes': [],
                        'jockey_win_percentage': 0.12,
                        'trainer_win_percentage': 0.15,
                        'field_size': len([l for l in lines if re.search(r'[A-Za-z].*\d', l)]),
                        'race_distance': 8.0,
                        'track_condition': 'fast',
                        'speed_rating': 75
                    }
                    
                    # Use first few reasonable numbers as recent form
                    form_numbers = []
                    for num in numbers[:6]:
                        try:
                            n = float(num)
                            if 1 <= n <= 20:
                                form_numbers.append(int(n))
                        except:
                            continue
                    
                    horse_data['recent_finishes'] = form_numbers[:3] if form_numbers else [5, 5, 5]
                    horses.append(horse_data)
    
    return horses[:20]  # Limit to 20 horses max

def main():
    st.title("🏇 Universal Horse Racing Predictor")
    st.subheader("🌍 Analyze ANY Racing Format from ANY Track Worldwide")

    # Universal race setup
    with st.sidebar:
        st.header("🏁 Universal Race Setup")
        race_name = st.text_input("Race Name/Track", "Universal Race")
        race_country = st.selectbox("Country/Region", 
                                   ["Venezuela", "USA", "UK", "Australia", "Japan", "Other"])
        distance = st.number_input("Distance (furlongs)", 5.0, 14.0, 8.0, 0.5)
        surface = st.selectbox("Surface", ["Dirt", "Turf", "All-Weather"])
        field_size = st.number_input("Expected Field Size", 4, 20, 8)

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("📄 Upload ANY Racing Document")
        
        st.markdown("""
        ### 🌍 Universal Support:
        - **Venezuela:** La Rinconada, Valencia
        - **USA:** Churchill Downs, Santa Anita, Belmont
        - **UK:** Ascot, Cheltenham, Aintree  
        - **Australia:** Flemington, Randwick
        - **Japan:** Tokyo, Nakayama
        - **ANY OTHER TRACK worldwide!**
        
        ### 📋 Supported Formats:
        - Race programs (any track)
        - Past performances (any source)
        - Race cards (any format)
        - PDFs, text files, copy-paste
        """)

        # File upload
        uploaded_file = st.file_uploader(
            "📁 Upload racing document (PDF, TXT, CSV)",
            type=['pdf', 'txt', 'csv'],
            help="Works with ANY racing format worldwide"
        )

        if uploaded_file is not None:
            with st.spinner("🔍 Analyzing racing document format..."):
                # Extract text from file
                text_content = ""
                try:
                    # Try different methods to read the file
                    if uploaded_file.name.lower().endswith('.txt'):
                        text_content = uploaded_file.read().decode('utf-8')
                    elif uploaded_file.name.lower().endswith('.csv'):
                        import pandas as pd
                        df = pd.read_csv(uploaded_file)
                        text_content = df.to_string()
                    else:
                        # Try to read as text (works for many PDFs)
                        content = uploaded_file.read()
                        try:
                            text_content = content.decode('utf-8', errors='ignore')
                        except:
                            text_content = content.decode('latin-1', errors='ignore')
                except Exception as e:
                    st.error(f"❌ Could not read file: {str(e)}")
                
                if text_content:
                    st.success("✅ File loaded successfully!")
                    
                    # Show preview
                    with st.expander("👀 Preview extracted text"):
                        st.text(text_content[:500] + "..." if len(text_content) > 500 else text_content)
                    
                    # Extract horses
                    horses = extract_universal_racing_data(text_content)
                    
                    if horses:
                        st.success(f"🐎 Found {len(horses)} horses!")
                        
                        # Show extracted horses
                        with st.expander("📋 View extracted horses"):
                            for i, horse in enumerate(horses, 1):
                                col_h1, col_h2 = st.columns(2)
                                with col_h1:
                                    st.write(f"**{i}. {horse['name']}**")
                                    st.caption(f"Post: {horse['post_position']} | Weight: {horse['weight']}kg")
                                with col_h2:
                                    st.caption(f"Recent: {horse['recent_finishes']}")
                        
                        if st.button("🚀 Analyze Race", type="primary"):
                            st.session_state.horses = horses
                            st.session_state.race_loaded = True
                            st.rerun()
                    else:
                        st.warning("⚠️ Could not extract horse data. Try manual input below.")

        # Manual input section (Universal format)
        st.markdown("### 📝 Manual Input (Works with ANY format)")
        st.markdown("""
        **Copy and paste directly from your racing source:**
        
        **Examples of what works:**
        - Horse Name, Post, Weight, Recent Finishes
        - MULTIVERSO 55 1;2;1 8
        - Thunder Strike, 3, 95, 1,2,3
        - Any tabular format with horse names and numbers
        """)
        
        universal_sample = """MULTIVERSO 55 1;2;1 8
MANCHEGA 53 3;4;2 10  
FURIA 55.5 1;2;3 1
CARAMEL LOVE 53 5;3;2 6
SALOME 55.5 3;5;4 4
PRIORITISE 53.5 2;1;3 2
PRINCESA SUSEJ 58 1;4;2 13
MISS UNIVERSO 53 4;3;5 14
MI QUERIDA MONTSE 53 2;3;1 3
RENACER 53 3;2;4 5
REINA FABRICIA 53 1;3;2 7
FANTASTIC SHOT 54 2;1;3 9
MISTICA 53 4;2;1 11
COACH SESSA 56 1;2;3 12"""

        universal_input = st.text_area(
            "📋 Paste ANY racing data format:",
            value=universal_sample,
            height=200,
            help="Works with any format - just include horse names and numbers"
        )
        
        if st.button("🚀 Analyze Universal Format"):
            horses = extract_universal_racing_data(universal_input)
            if horses:
                st.session_state.horses = horses
                st.session_state.race_loaded = True
                st.rerun()
            else:
                st.error("❌ Could not parse format. Try simpler format: Name, Weight, Recent, Post")

    with col2:
        st.header("📊 Race Overview")
        
        if 'horses' in st.session_state and st.session_state.horses:
            horses = st.session_state.horses
            st.metric("Total Horses", len(horses))
            st.metric("Distance", f"{distance} furlongs")
            st.metric("Surface", surface)
            
            st.subheader("🐎 Entries Found:")
            for i, horse in enumerate(horses, 1):
                with st.expander(f"{i}. {horse['name']}"):
                    st.write(f"**Post:** {horse['post_position']}")
                    st.write(f"**Weight:** {horse['weight']}kg")
                    st.write(f"**Recent:** {horse['recent_finishes']}")
                    if horse.get('jockey'):
                        st.write(f"**Jockey:** {horse['jockey']}")
        else:
            st.info("📄 Upload racing document to analyze")

    # AI Analysis Section
    if 'horses' in st.session_state and len(st.session_state.horses) >= 2:
        st.header("🔮 Universal AI Race Analysis")
        
        predictor = UniversalHorseRacingPredictor()
        
        # Update with race conditions
        for horse in st.session_state.horses:
            horse['race_distance'] = distance
            horse['track_condition'] = surface.lower().replace('-', '_')
            horse['field_size'] = len(st.session_state.horses)
        
        predictions = predictor.predict_universal_race(st.session_state.horses)
        
        st.subheader("🏆 Universal Predictions")
        
        col_pred1, col_pred2 = st.columns([1, 1])
        
        with col_pred1:
            # Create display data
            display_data = []
            for horse in predictions:
                display_data.append({
                    'Rank': predictions.index(horse) + 1,
                    'Horse': horse['Horse'],
                    'Post': horse['Post_Position'],
                    'Win%': horse['Win_Probability'],
                    'Score': horse['Score'],
                    'Analysis': horse['Analysis'][:30] + "..." if len(horse['Analysis']) > 30 else horse['Analysis']
                })
            
            # Simple text table
            st.text("Rank | Horse               |Post|Win%|Score|Analysis")
            st.text("-" * 55)
            for item in display_data[:8]:
                st.text(f"{item['Rank']:4} | {item['Horse'][:17]:17} | {item['Post']:4} | {item['Win%']:3} | {item['Score']:5} | {item['Analysis']}")
        
        with col_pred2:
            # Simple text-based chart
            st.text("Win Probability Visualization:")
            for horse in predictions[:6]:
                bar_length = int(horse['Win_Probability'] / 2)
                bar = "█" * bar_length + "░" * (25 - bar_length)
                st.text(f"{horse['Horse'][:15]:15} |{bar}| {horse['Win_Probability']}%")

        # Detailed analysis
        with st.expander("📈 Detailed Analysis"):
            for idx, horse in enumerate(predictions[:5], 1):
                col_det1, col_det2 = st.columns([1, 2])
                
                with col_det1:
                    st.subheader(f"{idx}. {horse['Horse']}")
                    st.metric("Win Probability", f"{horse['Win_Probability']}%")
                    st.metric("AI Score", horse['Score'])
                
                with col_det2:
                    st.write("**Universal Metrics:**")
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric("Post Position", horse['Post_Position'])
                    with cols[1]:
                        st.metric("Weight", f"{horse['Weight']}kg")
                    with cols[2]:
                        st.metric("Recent Form", str(horse['Recent_Form']))
                
                st.write(f"**Analysis:** {horse['Analysis']}")
                st.divider()

        # Universal betting recommendations
        st.header("💰 Universal Betting Strategy")
        
        col_bet1, col_bet2, col_bet3 = st.columns(3)
        
        with col_bet1:
            favorite = predictions[0]
            st.metric("🏆 Win Bet", favorite['Horse'], f"{favorite['Win_Probability']}%")
        
        with col_bet2:
            if len(predictions) > 1:
                exacta_key = predictions[:2]
                exacta_names = ", ".join([h['Horse'].split()[0] for h in exacta_key])
                st.metric("💎 Exacta Key", exacta_names, "Top 2")
        
        with col_bet3:
            longshots = [p for p in predictions if 5 < p['Win_Probability'] < 15]
            if longshots:
                longshot_names = ", ".join([h['Horse'].split()[0] for h in longshots[:2]])
                st.metric("🎯 Value Plays", longshot_names, "5-15%")

        # Export functionality
        st.header("📁 Export Results")
        
        export_data = []
        for idx, horse in enumerate(predictions, 1):
            export_data.append({
                'Rank': idx,
                'Horse': horse['Horse'],
                'Post_Position': horse['Post_Position'],
                'Win_Probability': horse['Win_Probability'],
                'Score': horse['Score'],
                'Weight': horse['Weight'],
                'Recent_Form': str(horse['Recent_Form']),
                'Analysis': horse['Analysis']
            })
        
        # Simple CSV export (without pandas)
        csv_lines = ["Rank,Horse,Post_Position,Win_Probability,Score,Weight,Recent_Form,Analysis"]
        for item in export_data:
            line = f"{item['Rank']},{item['Horse']},{item['Post_Position']},{item['Win_Probability']},{item['Score']},{item['Weight']},\"{item['Recent_Form']}\",\"{item['Analysis']}\""
            csv_lines.append(line)
        
        csv_content = "\n".join(csv_lines)
        
        st.download_button(
            label="📊 Download Universal Predictions CSV",
            data=csv_content,
            file_name=f"universal_race_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🏇 Universal Horse Racing AI - Works with ANY format worldwide</p>
        <p>Venezuela • USA • UK • Australia • Japan • Any Track • Any Format</p>
        <p><strong>Remember:</strong> This is for entertainment purposes. Always gamble responsibly.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
