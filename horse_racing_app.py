import streamlit as st
import pandas as pd
import PyPDF2
import re
from datetime import datetime

st.set_page_config(
    page_title="🐎 KimiK2 Horse Racing Predictor",
    page_icon="🐎",
    layout="wide"
)

class HorseRacingPredictor:
    def __init__(self):
        self.weights = {
            'speed_figure': 0.25, 'recent_form': 0.20, 'class_level': 0.15,
            'jockey_skill': 0.12, 'trainer_stats': 0.12, 'post_position': 0.08,
            'track_condition': 0.05, 'distance_fitness': 0.03
        }
        
        self.track_variants = {
            'fast': 1.0, 'good': 1.02, 'sloppy': 1.05, 
            'muddy': 1.08, 'turf_firm': 0.98, 'turf_good': 1.0
        }
        
        self.post_position_weights = {
            1: 0.95, 2: 0.97, 3: 0.98, 4: 0.99, 5: 1.0,
            6: 0.99, 7: 0.97, 8: 0.95, 9: 0.93, 10: 0.90,
            11: 0.87, 12: 0.83, 13: 0.79, 14: 0.75, 15: 0.70
        }

    def calculate_speed_score(self, horse_data):
        base_speed = horse_data.get('beyer_speed_figure', 70)
        track_adj = self.track_variants.get(horse_data.get('track_condition', 'fast'), 1.0)
        distance = horse_data.get('race_distance', 6.0)
        distance_factor = 1.0 if distance <= 8.0 else 0.95
        recent_speeds = horse_data.get('recent_beyer_figures', [base_speed])
        trend_factor = 1.0
        if len(recent_speeds) >= 3:
            trend = (recent_speeds[-1] - recent_speeds[-3]) / recent_speeds[-3]
            trend_factor = 1.0 + (trend * 0.3)
        return min(base_speed * track_adj * distance_factor * trend_factor, 120)

    def calculate_form_score(self, horse_data):
        recent_finishes = horse_data.get('recent_finishes', [5, 5, 5])
        total_races = len(recent_finishes)
        if total_races == 0:
            return 0.5
        weighted_sum = 0
        total_weight = 0
        for i, finish in enumerate(reversed(recent_finishes)):
            weight = (i + 1) / total_races
            position_score = max(0, (10 - finish) / 10)
            weighted_sum += position_score * weight
            total_weight += weight
        return weighted_sum / total_weight if total_weight > 0 else 0.5

    def calculate_class_score(self, horse_data):
        current_class = horse_data.get('race_class', 'claiming')
        horse_class = horse_data.get('horse_class', 'claiming')
        class_hierarchy = {
            'maiden': 1, 'claiming': 2, 'allowance': 3, 
            'stakes': 4, 'graded_stakes': 5, 'grade_1': 6
        }
        race_level = class_hierarchy.get(current_class, 2)
        horse_level = class_hierarchy.get(horse_class, 2)
        if horse_level > race_level:
            return 1.2
        elif horse_level == race_level:
            return 1.0
        else:
            return 0.8

    def calculate_connection_score(self, horse_data):
        jockey_win_pct = horse_data.get('jockey_win_percentage', 0.10)
        trainer_win_pct = horse_data.get('trainer_win_percentage', 0.12)
        jockey_score = min(jockey_win_pct / 0.25, 1.0)
        trainer_score = min(trainer_win_pct / 0.25, 1.0)
        combo_success = horse_data.get('jockey_trainer_combo_win_pct', 0.10)
        combo_bonus = min(combo_success / 0.30, 0.2)
        return jockey_score + (combo_bonus * 0.5), trainer_score + (combo_bonus * 0.5)

    def calculate_post_position_score(self, horse_data):
        post = horse_data.get('post_position', 5)
        field_size = horse_data.get('field_size', 10)
        if field_size <= 6:
            return 1.0
        elif field_size <= 10:
            return self.post_position_weights.get(post, 0.90)
        else:
            return self.post_position_weights.get(post, 0.80)

    def calculate_overall_score(self, horse_data):
        speed_score = self.calculate_speed_score(horse_data)
        form_score = self.calculate_form_score(horse_data)
        class_score = self.calculate_class_score(horse_data)
        jockey_score, trainer_score = self.calculate_connection_score(horse_data)
        post_score = self.calculate_post_position_score(horse_data)
        
        total_score = (
            speed_score * self.weights['speed_figure'] +
            form_score * 100 * self.weights['recent_form'] +
            class_score * 100 * self.weights['class_level'] +
            jockey_score * 100 * self.weights['jockey_skill'] +
            trainer_score * 100 * self.weights['trainer_stats'] +
            post_score * 100 * self.weights['post_position']
        )
        return total_score

    def predict_race(self, horses_data):
        results = []
        for horse in horses_data:
            score = self.calculate_overall_score(horse)
            results.append({
                'Horse': horse.get('name', 'Unknown'),
                'Score': round(score, 2),
                'Win_Probability': round(max(0, score - 70), 1),
                'Beyer_Figure': round(self.calculate_speed_score(horse), 1),
                'Form_Score': round(self.calculate_form_score(horse), 3),
                'Class_Score': round(self.calculate_class_score(horse), 3),
                'Jockey_Score': round(self.calculate_connection_score(horse)[0], 3),
                'Trainer_Score': round(self.calculate_connection_score(horse)[1], 3),
                'Post_Advantage': round(self.calculate_post_position_score(horse), 3)
            })
        
        results.sort(key=lambda x: x['Score'], reverse=True)
        total_prob = sum([r['Win_Probability'] for r in results])
        if total_prob > 0:
            for result in results:
                result['Win_Probability'] = (result['Win_Probability'] / total_prob * 100).round(1)
        return results

def extract_race_data_from_pdf(pdf_file):
    """Extract race data from PDF file"""
    horses = []
    
    try:
        # Read PDF
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        # Common patterns for horse racing data
        patterns = [
            # Pattern 1: Horse, Beyer, Finishes, Post, Jockey%, Trainer%
            r'([A-Za-z\s\']+)\s*,?\s*(\d+)\s*,?\s*([\d;]+)\s*,?\s*(\d+)\s*,?\s*(\d+(?:\.\d+)?)\s*,?\s*(\d+(?:\.\d+)?)',
            # Pattern 2: Simpler format - Horse, Speed, Post, Jockey
            r'([A-Za-z\s\']+)\s+(\d+)\s+([\d;]+)\s+(\d+)\s+(\d+(?:\.\d+)?)',
            # Pattern 3: Tabular format
            r'(\d+)\s+([A-Za-z\s\']+)\s+(\d+)\s+([\d;]+)\s+(\d+(?:\.\d+)?)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    if len(match) >= 5:
                        # Determine which pattern matched
                        if match[0].isdigit():  # Pattern 3 (starts with number)
                            horse_data = {
                                'name': match[1].strip(),
                                'beyer_speed_figure': int(match[2]),
                                'recent_finishes': [int(x.strip()) for x in match[3].split(';')],
                                'post_position': int(match[0]),
                                'jockey_win_percentage': float(match[4]) / 100,
                                'trainer_win_percentage': float(match[4]) / 100,
                                'race_class': 'allowance',
                                'horse_class': 'allowance',
                                'field_size': 8,
                                'race_distance': 8.0,
                                'track_condition': 'fast'
                            }
                        else:  # Pattern 1 or 2
                            horse_data = {
                                'name': match[0].strip(),
                                'beyer_speed_figure': int(match[1]),
                                'recent_finishes': [int(x.strip()) for x in match[2].split(';')],
                                'post_position': int(match[3]),
                                'jockey_win_percentage': float(match[4]) / 100,
                                'trainer_win_percentage': float(match[5]) / 100 if len(match) > 5 else float(match[4]) / 100,
                                'race_class': 'allowance',
                                'horse_class': 'allowance',
                                'field_size': 8,
                                'race_distance': 8.0,
                                'track_condition': 'fast'
                            }
                        horses.append(horse_data)
                except:
                    continue
        
        # If no pattern matches, try simple line-by-line parsing
        if not horses:
            lines = text.split('\n')
            for line in lines:
                # Try to find any line with numbers and horse names
                numbers = re.findall(r'\d+', line)
                words = re.findall(r'[A-Za-z]+', line)
                
                if len(numbers) >= 3 and len(words) >= 1:
                    try:
                        horse_data = {
                            'name': ' '.join(words[:2]),  # First 1-2 words as name
                            'beyer_speed_figure': int(numbers[0]),
                            'recent_finishes': [int(numbers[1])],
                            'post_position': int(numbers[2]),
                            'jockey_win_percentage': 0.12,
                            'trainer_win_percentage': 0.15,
                            'race_class': 'allowance',
                            'horse_class': 'allowance',
                            'field_size': len(lines),
                            'race_distance': 8.0,
                            'track_condition': 'fast'
                        }
                        horses.append(horse_data)
                    except:
                        continue
    
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
    
    return horses

def main():
    st.set_page_config(
        page_title="🐎 KimiK2 Horse Racing Predictor",
        page_icon="🐎",
        layout="wide"
    )

    st.title("🏇 KimiK2 Horse Racing Predictor")
    st.subheader("📄 Upload Race PDF for AI Analysis")

    # Race setup
    with st.sidebar:
        st.header("🏁 Race Information")
        race_name = st.text_input("Race Name", "KimiK2 Challenge Stakes")
        track_name = st.text_input("Track Name", "Virtual Downs")
        distance = st.number_input("Distance (furlongs)", 6.0, 12.0, 8.5, 0.5)
        track_condition = st.selectbox("Track Condition", 
                                     ["Fast", "Good", "Sloppy", "Muddy", "Turf-Firm", "Turf-Good"])

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("📄 Upload Race PDF")
        
        st.markdown("""
        ### Upload your race program or past performances PDF:
        
        **Supported formats:**
        - Race programs (Equibase, Daily Racing Form, etc.)
        - Past performance PDFs
        - Race cards from tracks
        
        **The PDF should contain:**
        - Horse names
        - Beyer Speed Figures
        - Recent finishing positions
        - Post positions
        - Jockey/trainer statistics
        """)

        # File upload
        uploaded_file = st.file_uploader(
            "📁 Choose a PDF file",
            type=['pdf'],
            help="Upload a race program or past performances PDF"
        )

        if uploaded_file is not None:
            with st.spinner("🔍 Extracting race data from PDF..."):
                horses = extract_race_data_from_pdf(uploaded_file)
                
                if horses:
                    st.success(f"✅ Found {len(horses)} horses in the PDF!")
                    
                    # Show extracted data
                    with st.expander("📋 View Extracted Data"):
                        for i, horse in enumerate(horses, 1):
                            st.write(f"{i}. **{horse['name']}**")
                            st.caption(f"   Speed: {horse['beyer_speed_figure']} | Post: {horse['post_position']} | Recent: {horse['recent_finishes']}")
                    
                    if st.button("🚀 Analyze Race", type="primary"):
                        st.session_state.horses = horses
                        st.session_state.race_loaded = True
                        st.rerun()
                else:
                    st.warning("⚠️ Could not extract horse data from PDF. Please check the format.")
                    
                    # Manual input fallback
                    st.markdown("### 📝 Manual Input Fallback")
                    st.markdown("Since the PDF couldn't be parsed automatically, you can copy-paste the data:")
                    
                    manual_input = st.text_area(
                        "Paste race data here (Horse Name, Beyer, Recent Finishes, Post, Jockey%, Trainer%):",
                        height=150,
                        help="Format: Horse Name, 95, 1;2;1, 3, 22, 18"
                    )
                    
                    if st.button("Analyze Manually Entered Data"):
                        horses = parse_manual_data(manual_input)
                        if horses:
                            st.session_state.horses = horses
                            st.session_state.race_loaded = True
                            st.rerun()

        # Sample data section
        with st.expander("📝 Don't have a PDF? Use sample data"):
            st.markdown("""
            ### Sample Race Data Format:
            ```
            Thunder Strike, 95, 1;2;1, 3, 22, 18
            Lightning Bolt, 93, 2;1;2, 7, 18, 25
            Desert Storm, 88, 3;3;4, 2, 15, 20
            Morning Glory, 91, 4;2;1, 10, 20, 16
            Royal Command, 90, 1;4;3, 5, 12, 24
            ```
            """)
            
            sample_data = """Thunder Strike, 95, 1;2;1, 3, 22, 18
Lightning Bolt, 93, 2;1;2, 7, 18, 25
Desert Storm, 88, 3;3;4, 2, 15, 20
Morning Glory, 91, 4;2;1, 10, 20, 16
Royal Command, 90, 1;4;3, 5, 12, 24
Speed Demon, 89, 2;1;2, 1, 25, 14
Golden Arrow, 87, 5;3;2, 8, 16, 19
Silver Streak, 86, 3;5;4, 12, 14, 17"""
            
            manual_input = st.text_area("Or paste data here:", value=sample_data, height=150)
            
            if st.button("Analyze Sample Data"):
                horses = parse_manual_data(manual_input)
                if horses:
                    st.session_state.horses = horses
                    st.session_state.race_loaded = True
                    st.rerun()

    with col2:
        st.header("📊 Race Overview")
        
        if 'horses' in st.session_state and st.session_state.horses:
            horses = st.session_state.horses
            st.metric("Total Horses", len(horses))
            st.metric("Race Distance", f"{distance} furlongs")
            st.metric("Track Condition", track_condition)
            
            st.subheader("🐎 Race Entries:")
            for i, horse in enumerate(horses, 1):
                with st.expander(f"{i}. {horse['name']}"):
                    st.write(f"**Speed:** {horse['beyer_speed_figure']}")
                    st.write(f"**Post:** {horse['post_position']}")
                    st.write(f"**Recent:** {horse['recent_finishes']}")
                    st.write(f"**Jockey:** {horse['jockey_win_percentage']*100:.1f}%")
                    st.write(f"**Trainer:** {horse['trainer_win_percentage']*100:.1f}%")
        else:
            st.info("📄 Upload a PDF to see race entries")

    # AI Analysis Section
    if 'horses' in st.session_state and len(st.session_state.horses) >= 2:
        st.header("🔮 AI Race Analysis")
        
        predictor = HorseRacingPredictor()
        
        # Update horses with race conditions
        for horse in st.session_state.horses:
            horse['race_distance'] = distance
            horse['track_condition'] = track_condition.lower().replace('-', '_')
            horse['field_size'] = len(st.session_state.horses)
        
        predictions = predictor.predict_race(st.session_state.horses)
        
        st.subheader("🏆 Final Predictions")
        
        col_pred1, col_pred2 = st.columns([1, 1])
        
        with col_pred1:
            # Results table
            results_df = pd.DataFrame(predictions)
            display_cols = ['Horse', 'Win_Probability', 'Score', 'Beyer_Figure']
            st.dataframe(results_df[display_cols].head(8))
        
        with col_pred2:
            # Bar chart
            chart_data = pd.DataFrame({
                'Horse': [p['Horse'] for p in predictions[:8]],
                'Win Probability': [p['Win_Probability'] for p in predictions[:8]]
            })
            st.bar_chart(chart_data.set_index('Horse'))

        # Detailed analysis
        with st.expander("📈 Detailed Horse Analysis"):
            for idx, horse in enumerate(predictions[:5], 1):
                col_det1, col_det2 = st.columns([1, 2])
                
                with col_det1:
                    st.subheader(f"{idx}. {horse['Horse']}")
                    st.metric("Win Probability", f"{horse['Win_Probability']}%")
                    st.metric("AI Score", horse['Score'])
                
                with col_det2:
                    st.write("**Performance Metrics:**")
                    cols = st.columns(4)
                    with cols[0]:
                        st.metric("Speed", horse['Beyer_Figure'])
                    with cols[1]:
                        st.metric("Form", f"{horse['Form_Score']:.3f}")
                    with cols[2]:
                        st.metric("Class", f"{horse['Class_Score']:.3f}")
                    with cols[3]:
                        st.metric("Post", f"{horse['Post_Advantage']:.3f}")
                
                st.divider()

        # Betting Strategy
        st.header("💰 AI Betting Recommendations")
        
        col_bet1, col_bet2, col_bet3 = st.columns(3)
        
        with col_bet1:
            favorite = predictions[0]
            st.metric("🏆 Win Bet", favorite['Horse'], f"{favorite['Win_Probability']}%")
        
        with col_bet2:
            if len(predictions) > 1:
                value_play = predictions[1] if predictions[1]['Win_Probability'] > 15 else predictions[0]
                st.metric("💎 Exacta Key", value_play['Horse'], f"{value_play['Win_Probability']}%")
        
        with col_bet3:
            longshots = [p for p in predictions if 3 < p['Win_Probability'] < 10]
            if longshots:
                longshot = longshots[-1]
                st.metric("🚀 Longshot", longshot['Horse'], f"{longshot['Win_Probability']}%")

        # Export results
        st.header("📁 Export Predictions")
        
        export_data = []
        for idx, horse in enumerate(predictions, 1):
            export_data.append({
                'Rank': idx,
                'Horse': horse['Horse'],
                'Win_Probability': horse['Win_Probability'],
                'Score': horse['Score'],
                'Beyer_Figure': horse['Beyer_Figure'],
                'Form_Score': horse['Form_Score'],
                'Class_Score': horse['Class_Score'],
                'Jockey_Score': horse['Jockey_Score'],
                'Trainer_Score': horse['Trainer_Score'],
                'Post_Advantage': horse['Post_Advantage']
            })
        
        csv_df = pd.DataFrame(export_data)
        csv = csv_df.to_csv(index=False)
        
        st.download_button(
            label="📊 Download Race Predictions CSV",
            data=csv,
            file_name=f"race_predictions_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🏇 Powered by KimiK2 AI Horse Racing Analysis System</p>
        <p>Supports: Race programs, past performances, and PDF race cards</p>
        <p><strong>Remember:</strong> This is for entertainment purposes. Always gamble responsibly.</p>
    </div>
    """, unsafe_allow_html=True)

def parse_manual_data(text_data):
    """Parse manually entered race data"""
    horses = []
    lines = text_data.strip().split('\n')
    
    for line in lines:
        if not line.strip():
            continue
            
        parts = line.split(',')
        if len(parts) >= 5:
            try:
                horse_data = {
                    'name': parts[0].strip(),
                    'beyer_speed_figure': int(parts[1].strip()),
                    'recent_finishes': [int(x.strip()) for x in parts[2].split(';')],
                    'post_position': int(parts[3].strip()),
                    'jockey_win_percentage': float(parts[4].strip()) / 100,
                    'trainer_win_percentage': float(parts[5].strip()) / 100 if len(parts) > 5 else float(parts[4].strip()) / 100,
                    'race_class': 'allowance',
                    'horse_class': 'allowance',
                    'field_size': len(lines),
                    'race_distance': 8.0,
                    'track_condition': 'fast'
                }
                horses.append(horse_data)
            except:
                continue
    
    return horses

if __name__ == "__main__":
    main()
