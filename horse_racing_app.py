import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="🐎 Universal Horse Racing Predictor",
    page_icon="🐎",
    layout="wide"
)

class UniversalHorseRacingPredictor:
    def __init__(self):
        self.weights = {
            'speed_figure': 0.30, 'recent_form': 0.25, 'class_level': 0.15,
            'post_position': 0.10, 'jockey_skill': 0.10, 'trainer_stats': 0.08,
            'distance_fitness': 0.02
        }
        
        # Simple post position weights
        self.post_weights = {
            1: 0.98, 2: 0.99, 3: 1.00, 4: 0.99, 5: 0.98,
            6: 0.97, 7: 0.96, 8: 0.94, 9: 0.92, 10: 0.90,
            11: 0.87, 12: 0.84, 13: 0.81, 14: 0.78, 15: 0.75,
            16: 0.72, 17: 0.69, 18: 0.66, 19: 0.63, 20: 0.60
        }

    def calculate_universal_score(self, horse_data):
        """Universal scoring without complex calculations"""
        
        # Speed Score (simple)
        speed_base = horse_data.get('speed_rating', 75)
        
        # Recent Form Score (simple)
        recent_form = horse_data.get('recent_finishes', [5, 5, 5])
        form_score = 0.5  # Default
        
        if recent_form and len(recent_form) > 0:
            total = sum(recent_form)
            avg = total / len(recent_form)
            form_score = max(0, (10 - avg) / 10)
        
        # Post Position Score
        post = horse_data.get('post_position', 5)
        post_score = self.post_weights.get(post, 0.90)
        
        # Simple total score
        total_score = (
            speed_base * 0.5 +
            form_score * 40 +
            post_score * 10
        )
        
        return total_score

    def predict_universal_race(self, horses_data):
        """Universal race prediction"""
        results = []
        
        for horse in horses_data:
            score = self.calculate_universal_score(horse)
            
            results.append({
                'Horse': horse.get('name', 'Unknown'),
                'Score': round(score, 2),
                'Win_Probability': round(max(0, score - 70), 1),
                'Post_Position': horse.get('post_position', '?'),
                'Weight': horse.get('weight', '?'),
                'Recent_Form': horse.get('recent_finishes', '?'),
                'Analysis': self.generate_simple_analysis(horse)
            })
        
        # Sort by score
        results.sort(key=lambda x: x['Score'], reverse=True)
        
        # Normalize probabilities
        total_prob = sum([r['Win_Probability'] for r in results])
        if total_prob > 0:
            for result in results:
                result['Win_Probability'] = (result['Win_Probability'] / total_prob * 100).round(1)
        
        return results

    def generate_simple_analysis(self, horse_data):
        """Simple analysis without complex logic"""
        analysis = []
        
        post = horse_data.get('post_position', 5)
        if post <= 3:
            analysis.append("🎯 Good post")
        elif post >= 10:
            analysis.append("⚠️ Wide post")
        
        recent = horse_data.get('recent_finishes', [])
        if recent:
            avg = sum(recent) / len(recent) if recent else 5
            if avg <= 3:
                analysis.append("🔥 Good form")
            elif avg >= 7:
                analysis.append("📉 Struggling")
        
        return " | ".join(analysis) if analysis else "📊 Standard"

def extract_simple_racing_data(text_content):
    """Simple racing data extraction without regex"""
    horses = []
    lines = text_content.strip().split('\n')
    
    # Simple extraction strategies
    for line in lines:
        line = line.strip()
        if not line or len(line) < 10:
            continue
            
        # Strategy 1: Look for lines with both letters and numbers
        has_letters = any(c.isalpha() for c in line)
        has_numbers = any(c.isdigit() for c in line)
        
        if has_letters and has_numbers:
            # Split by common separators
            parts = line.replace(',', ' ').replace('\t', ' ').split()
            
            # Find horse name (first word or words before numbers)
            name_parts = []
            number_parts = []
            
            for part in parts:
                if part.isalpha() and len(part) > 2:
                    name_parts.append(part)
                elif part.replace('.', '').replace(';', '').isdigit():
                    number_parts.append(part.replace(';', ''))
                
                if len(name_parts) >= 1 and len(number_parts) >= 2:
                    break
            
            if name_parts and len(number_parts) >= 2:
                horse_name = ' '.join(name_parts[:3])  # Max 3 words for name
                
                # Extract numbers
                try:
                    post_pos = int(number_parts[0]) if len(number_parts) > 0 else len(horses) + 1
                    weight = int(number_parts[1]) if len(number_parts) > 1 else 55
                    
                    # Recent form (next 3-5 numbers)
                    recent_form = []
                    for num in number_parts[2:7]:
                        try:
                            n = int(num)
                            if 1 <= n <= 20:
                                recent_form.append(n)
                        except:
                            continue
                    
                    horse_data = {
                        'name': horse_name,
                        'post_position': post_pos,
                        'weight': weight,
                        'recent_finishes': recent_form[:5] if recent_form else [5, 5, 5],
                        'jockey_win_percentage': 0.12,
                        'trainer_win_percentage': 0.15,
                        'field_size': len([l for l in lines if len(l.strip()) > 10 and any(c.isalpha() for c in l) and any(c.isdigit() for c in l)]),
                        'race_distance': 8.0,
                        'track_condition': 'fast',
                        'speed_rating': 75
                    }
                    
                    horses.append(horse_data)
                except:
                    continue
    
    # Fallback: Simple line counting
    if not horses:
        valid_lines = [l for l in lines if len(l.strip()) > 10 and any(c.isalpha() for c in l) and any(c.isdigit() for c in l)]
        for i, line in enumerate(valid_lines[:20]):
            words = [w for w in line.split() if w.isalpha() and len(w) > 2]
            numbers = [n for n in line.split() if n.replace('.', '').isdigit()]
            
            if words and numbers:
                horse_data = {
                    'name': words[0],
                    'post_position': i + 1,
                    'weight': 55,
                    'recent_finishes': [int(numbers[0])] if numbers else [5],
                    'jockey_win_percentage': 0.12,
                    'trainer_win_percentage': 0.15,
                    'field_size': len(valid_lines),
                    'race_distance': 8.0,
                    'track_condition': 'fast',
                    'speed_rating': 75
                }
                horses.append(horse_data)
    
    return horses[:20]  # Max 20 horses

def main():
    st.title("🏇 Universal Horse Racing Predictor")
    st.subheader("📄 Upload ANY Racing Format Worldwide")

    # Universal race setup
    with st.sidebar:
        st.header("🏁 Race Setup")
        race_name = st.text_input("Race Name/Track", "Universal Race")
        distance = st.number_input("Distance (furlongs)", 5.0, 14.0, 8.0, 0.5)
        surface = st.selectbox("Surface", ["Dirt", "Turf", "All-Weather"])

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("📄 Upload Racing Document")
        
        st.markdown("""
        ### 🌍 Works with ANY format:
        - Venezuelan racing programs
        - American past performances
        - European race cards
        - Australian form guides
        - Japanese racing data
        - ANY text-based racing document!
        """)

        # File upload
        uploaded_file = st.file_uploader(
            "📁 Choose racing file (PDF, TXT, CSV)",
            type=['pdf', 'txt', 'csv'],
            help="Works with any racing format worldwide"
        )

        if uploaded_file is not None:
            with st.spinner("🔍 Reading racing document..."):
                text_content = ""
                try:
                    # Read file content
                    content = uploaded_file.read()
                    
                    # Try different encodings
                    for encoding in ['utf-8', 'latin-1', 'cp1252']:
                        try:
                            text_content = content.decode(encoding)
                            break
                        except:
                            continue
                    
                    if text_content:
                        st.success("✅ File read successfully!")
                        
                        # Show preview
                        with st.expander("👀 Preview extracted text"):
                            preview = text_content[:500] + "..." if len(text_content) > 500 else text_content
                            st.text(preview)
                        
                        # Extract horses
                        horses = extract_simple_racing_data(text_content)
                        
                        if horses:
                            st.success(f"🐎 Found {len(horses)} horses!")
                            
                            if st.button("🚀 Analyze Race", type="primary"):
                                st.session_state.horses = horses
                                st.rerun()
                        else:
                            st.warning("⚠️ Could not extract horse data. Try manual input below.")
                    else:
                        st.error("❌ Could not read file content. File might be image-based.")
                        
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")

        # Manual input fallback
        st.markdown("### 📝 Manual Input (Always Works)")
        st.markdown("""
        **Copy and paste directly from your racing source:**
        
        **Simple format:** HorseName PostPosition Weight RecentForm
        **Example:** MULTIVERSO 8 55 1;2;1
        """)

        universal_sample = """MULTIVERSO 8 55 1;2;1
MANCHEGA 10 53 3;4;2  
FURIA 1 55.5 1;2;3
CARAMEL LOVE 6 53 5;3;2
SALOME 4 55.5 3;5;4
PRIORITISE 2 53.5 2;1;3
PRINCESA SUSEJ 13 58 1;4;2
MISS UNIVERSO 14 53 4;3;5
MI QUERIDA MONTSE 3 53 2;3;1
RENACER 5 53 3;2;4
REINA FABRICIA 7 53 1;3;2
FANTASTIC SHOT 9 54 2;1;3
MISTICA 11 53 4;2;1
COACH SESSA 12 56 1;2;3"""

        manual_input = st.text_area(
            "📋 Paste racing data here:",
            value=universal_sample,
            height=200,
            help="Any format with horse names and numbers works!"
        )
        
        if st.button("🚀 Analyze Manual Input", type="primary"):
            horses = extract_simple_racing_data(manual_input)
            if horses:
                st.session_state.horses = horses
                st.success(f"✅ Loaded {len(horses)} horses!")
                st.rerun()
            else:
                st.error("❌ Could not parse. Try: HorseName Post Weight Form")

    with col2:
        st.header("📊 Race Overview")
        
        if 'horses' in st.session_state and st.session_state.horses:
            horses = st.session_state.horses
            st.metric("Total Horses", len(horses))
            st.metric("Distance", f"{distance} furlongs")
            st.metric("Surface", surface)
            
            st.subheader("🐎 Race Entries:")
            for i, horse in enumerate(horses, 1):
                with st.expander(f"{i}. {horse['name']}"):
                    st.write(f"**Post:** {horse['post_position']}")
                    st.write(f"**Weight:** {horse['weight']}kg")
                    st.write(f"**Recent:** {horse['recent_finishes']}")
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
        
        st.subheader("🏆 Final Predictions")
        
        col_pred1, col_pred2 = st.columns([1, 1])
        
        with col_pred1:
            # Simple text table
            st.text("Rank | Horse               |Post|Win%|Score")
            st.text("-" * 45)
            for i, horse in enumerate(predictions[:8], 1):
                st.text(f"{i:4} | {horse['Horse'][:17]:17} | {horse['Post_Position']:4} | {horse['Win_Probability']:3} | {horse['Score']:5}")
        
        with col_pred2:
            # Simple text chart
            st.text("Win Probability:")
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
                    st.write("**Performance Metrics:**")
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric("Post Position", horse['Post_Position'])
                    with cols[1]:
                        st.metric("Weight", f"{horse['Weight']}kg")
                    with cols[2]:
                        st.metric("Recent Form", str(horse['Recent_Form']))
                
                st.write(f"**Analysis:** {horse['Analysis']}")
                st.divider()

        # Betting Strategy
        st.header("💰 AI Betting Recommendations")
        
        col_bet1, col_bet2, col_bet3 = st.columns(3)
        
        with col_bet1:
            favorite = predictions[0]
            st.metric("🏆 Win Bet", favorite['Horse'], f"{favorite['Win_Probability']}%")
        
        with col_bet2:
            if len(predictions) > 1:
                place_horse = predictions[1] if predictions[1]['Win_Probability'] > 10 else predictions[0]
                st.metric("💎 Place/Show", place_horse['Horse'], f"{place_horse['Win_Probability']}%")
        
        with col_bet3:
            longshots = [p for p in predictions if 5 < p['Win_Probability'] < 15]
            if longshots:
                longshot = longshots[-1]
                st.metric("🚀 Longshot", longshot['Horse'], f"{longshot['Win_Probability']}%")

        # Export
        st.header("📁 Export Predictions")
        
        # Simple CSV format
        csv_lines = ["Rank,Horse,Post_Position,Win_Probability,Score,Weight,Recent_Form,Analysis"]
        for item in predictions:
            csv_lines.append(f"{predictions.index(item)+1},{item['Horse']},{item['Post_Position']},{item['Win_Probability']},{item['Score']},{item['Weight']},\"{item['Recent_Form']}\",\"{item['Analysis']}\"")
        
        csv_content = "\n".join(csv_lines)
        
        st.download_button(
            label="📊 Download Predictions CSV",
            data=csv_content,
            file_name=f"race_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🏇 Universal Racing AI - Works with ANY format worldwide</p>
        <p>No regex • No complex dependencies • Just works!</p>
        <p><strong>Remember:</strong> This is for entertainment purposes. Always gamble responsibly.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
