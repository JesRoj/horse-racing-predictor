import streamlit as st

st.set_page_config(
    page_title="🐎 KimiK2 Horse Racing Predictor",
    page_icon="🐎",
    layout="wide"
)

class HorseRacingPredictor:
    def __init__(self):
        # Professional weights for horse racing analysis
        self.weights = {
            'speed_figure': 0.25,      # Beyer Speed Figure (most important)
            'recent_form': 0.20,       # Recent performance trend
            'class_level': 0.15,       # Class of competition
            'jockey_skill': 0.12,      # Jockey win percentage
            'trainer_stats': 0.12,     # Trainer win percentage
            'post_position': 0.08,     # Starting gate position
            'track_condition': 0.05,   # Surface and weather
            'distance_fitness': 0.03   # Performance at this distance
        }
        
        # Track condition adjustments
        self.track_variants = {
            'fast': 1.0, 'good': 1.02, 'sloppy': 1.05, 
            'muddy': 1.08, 'turf_firm': 0.98, 'turf_good': 1.0
        }
        
        # Post position advantages (inside posts are better)
        self.post_position_weights = {
            1: 0.95, 2: 0.97, 3: 0.98, 4: 0.99, 5: 1.0,
            6: 0.99, 7: 0.97, 8: 0.95, 9: 0.93, 10: 0.90,
            11: 0.87, 12: 0.83, 13: 0.79, 14: 0.75, 15: 0.70
        }

    def calculate_speed_score(self, horse_data):
        """Calculate speed-based score using Beyer Speed Figure principles"""
        base_speed = horse_data.get('beyer_speed_figure', 70)
        
        # Adjust for track condition
        track_adj = self.track_variants.get(horse_data.get('track_condition', 'fast'), 1.0)
        
        # Adjust for distance (horses perform differently at different distances)
        distance = horse_data.get('race_distance', 6.0)
        distance_factor = 1.0 if distance <= 8.0 else 0.95
        
        # Recent speed trend (improving horses get bonus)
        recent_speeds = horse_data.get('recent_beyer_figures', [base_speed])
        trend_factor = 1.0
        if len(recent_speeds) >= 3:
            trend = (recent_speeds[-1] - recent_speeds[-3]) / recent_speeds[-3]
            trend_factor = 1.0 + (trend * 0.3)  # Up to 30% bonus for improving trend
        
        adjusted_speed = base_speed * track_adj * distance_factor * trend_factor
        return min(adjusted_speed, 120)  # Cap at maximum reasonable figure

    def calculate_form_score(self, horse_data):
        """Calculate recent form score based on finishing positions"""
        recent_finishes = horse_data.get('recent_finishes', [5, 5, 5])
        total_races = len(recent_finishes)
        
        if total_races == 0:
            return 0.5
            
        # Weight recent races more heavily
        weighted_sum = 0
        total_weight = 0
        
        for i, finish in enumerate(reversed(recent_finishes)):
            weight = (i + 1) / total_races  # Recent races weighted more
            position_score = max(0, (10 - finish) / 10)  # Convert position to 0-1 scale
            weighted_sum += position_score * weight
            total_weight += weight
            
        return weighted_sum / total_weight if total_weight > 0 else 0.5

    def calculate_class_score(self, horse_data):
        """Calculate class level score (horses dropping in class have advantage)"""
        current_class = horse_data.get('race_class', 'claiming')
        horse_class = horse_data.get('horse_class', 'claiming')
        
        class_hierarchy = {
            'maiden': 1, 'claiming': 2, 'allowance': 3, 
            'stakes': 4, 'graded_stakes': 5, 'grade_1': 6
        }
        
        race_level = class_hierarchy.get(current_class, 2)
        horse_level = class_hierarchy.get(horse_class, 2)
        
        # Bonus for horses moving down in class (easier competition)
        if horse_level > race_level:
            return 1.2  # 20% bonus for dropping in class
        elif horse_level == race_level:
            return 1.0
        else:
            return 0.8  # Penalty for moving up in class

    def calculate_connection_score(self, horse_data):
        """Calculate jockey and trainer scores"""
        jockey_win_pct = horse_data.get('jockey_win_percentage', 0.10)
        trainer_win_pct = horse_data.get('trainer_win_percentage', 0.12)
        
        # Normalize to 0-1 scale (assuming 25% is excellent)
        jockey_score = min(jockey_win_pct / 0.25, 1.0)
        trainer_score = min(trainer_win_pct / 0.25, 1.0)
        
        # Bonus for jockey-trainer combination success
        combo_success = horse_data.get('jockey_trainer_combo_win_pct', 0.10)
        combo_bonus = min(combo_success / 0.30, 0.2)
        
        return jockey_score + (combo_bonus * 0.5), trainer_score + (combo_bonus * 0.5)

    def calculate_post_position_score(self, horse_data):
        """Calculate post position advantage score"""
        post = horse_data.get('post_position', 5)
        field_size = horse_data.get('field_size', 10)
        
        # Adjust weights based on field size
        if field_size <= 6:
            return 1.0  # Small field - inside posts less critical
        elif field_size <= 10:
            return self.post_position_weights.get(post, 0.90)
        else:
            # Large field - outside posts heavily penalized
            return self.post_position_weights.get(post, 0.80)

    def calculate_overall_score(self, horse_data):
        """Calculate comprehensive horse score using weighted factors"""
        speed_score = self.calculate_speed_score(horse_data)
        form_score = self.calculate_form_score(horse_data)
        class_score = self.calculate_class_score(horse_data)
        jockey_score, trainer_score = self.calculate_connection_score(horse_data)
        post_score = self.calculate_post_position_score(horse_data)
        
        # Apply professional weights to each factor
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
        """Predict race outcomes for all horses"""
        results = []
        
        for horse in horses_data:
            score = self.calculate_overall_score(horse)
            
            results.append({
                'Horse': horse.get('name', 'Unknown'),
                'Score': round(score, 2),
                'Win_Probability': round(max(0, score - 70), 1),  # Convert to percentage
                'Beyer_Figure': round(self.calculate_speed_score(horse), 1),
                'Form_Score': round(self.calculate_form_score(horse), 3),
                'Class_Score': round(self.calculate_class_score(horse), 3),
                'Jockey_Score': round(self.calculate_connection_score(horse)[0], 3),
                'Trainer_Score': round(self.calculate_connection_score(horse)[1], 3),
                'Post_Advantage': round(self.calculate_post_position_score(horse), 3),
                'Analysis': self.generate_horse_analysis(horse)
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['Score'], reverse=True)
        
        # Normalize probabilities to sum to 100%
        total_prob = sum([r['Win_Probability'] for r in results])
        if total_prob > 0:
            for result in results:
                result['Win_Probability'] = (result['Win_Probability'] / total_prob * 100).round(1)
        
        return results

    def generate_horse_analysis(self, horse_data):
        """Generate brief analysis for each horse"""
        speed = self.calculate_speed_score(horse_data)
        form = self.calculate_form_score(horse_data)
        post = self.calculate_post_position_score(horse_data)
        
        analysis = []
        
        if speed > 95:
            analysis.append("🔥 High speed figure")
        elif speed > 85:
            analysis.append("⚡ Good speed")
        else:
            analysis.append("🐌 Needs more speed")
            
        if form > 0.7:
            analysis.append("📈 Strong recent form")
        elif form > 0.5:
            analysis.append("📊 Consistent performer")
        else:
            analysis.append("📉 Struggling recently")
            
        if post > 0.95:
            analysis.append("🎯 Good post position")
        elif post < 0.85:
            analysis.append("⚠️ Wide post challenge")
            
        return " | ".join(analysis)

def main():
    st.title("🏇 KimiK2 Horse Racing Predictor")
    st.subheader("AI-Powered Race Analysis & Predictions")

    if 'horses' not in st.session_state:
        st.session_state.horses = []

    # Race setup section
    with st.sidebar:
        st.header("🏁 Race Setup")
        
        race_name = st.text_input("Race Name", "KimiK2 Challenge Stakes")
        track_name = st.text_input("Track Name", "Virtual Downs")
        distance = st.number_input("Distance (furlongs)", 6.0, 12.0, 8.5, 0.5)
        track_condition = st.selectbox("Track Condition", 
                                     ["Fast", "Good", "Sloppy", "Muddy", "Turf-Firm", "Turf-Good"])
        field_size = st.number_input("Field Size", 4, 16, 8)

    # Main horse input section
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("🐎 Add Horse")
        
        with st.expander("➕ Enter Horse Details", expanded=True):
            horse_name = st.text_input("Horse Name", key="horse_name")
            
            col_h1, col_h2 = st.columns(2)
            
            with col_h1:
                beyer_figure = st.number_input("Beyer Speed Figure", 50, 120, 85, key="beyer")
                recent_beyer = st.text_input("Recent Beyer Figures (e.g., 82,84,85)", "82,84,85", key="recent_beyer")
                recent_finishes = st.text_input("Recent Finishes (e.g., 2,1,3)", "2,1,3", key="recent_finishes")
            
            with col_h2:
                race_class = st.selectbox("Race Class", ["Maiden", "Claiming", "Allowance", "Stakes", "Graded Stakes"], key="race_class")
                horse_class = st.selectbox("Horse Class", ["Maiden", "Claiming", "Allowance", "Stakes", "Graded Stakes"], key="horse_class")
                post_position = st.number_input("Post Position", 1, field_size, 1, key="post_position")
            
            col_h3, col_h4 = st.columns(2)
            
            with col_h3:
                jockey_win_pct = st.number_input("Jockey Win %", 0.0, 50.0, 12.0, 0.1, key="jockey_pct") / 100
                trainer_win_pct = st.number_input("Trainer Win %", 0.0, 50.0, 15.0, 0.1, key="trainer_pct") / 100
            
            with col_h4:
                combo_win_pct = st.number_input("Jockey-Trainer Combo Win %", 0.0, 100.0, 20.0, 0.1, key="combo_pct") / 100
                race_distance = st.number_input("Race Distance (furlongs)", 5.0, 12.0, distance, 0.5, key="race_dist")

            if st.button("🐎 Add Horse to Race", type="primary"):
                if horse_name:
                    try:
                        recent_beyer_list = [int(x.strip()) for x in recent_beyer.split(',')]
                        recent_finishes_list = [int(x.strip()) for x in recent_finishes.split(',')]
                        
                        horse_data = {
                            'name': horse_name,
                            'beyer_speed_figure': beyer_figure,
                            'recent_beyer_figures': recent_beyer_list,
                            'recent_finishes': recent_finishes_list,
                            'race_class': race_class.lower().replace(' ', '_'),
                            'horse_class': horse_class.lower().replace(' ', '_'),
                            'jockey_win_percentage': jockey_win_pct,
                            'trainer_win_percentage': trainer_win_pct,
                            'jockey_trainer_combo_win_pct': combo_win_pct,
                            'post_position': post_position,
                            'field_size': field_size,
                            'race_distance': race_distance,
                            'track_condition': track_condition.lower().replace('-', '_')
                        }
                        
                        st.session_state.horses.append(horse_data)
                        st.success(f"✅ Added {horse_name} to the race!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error adding horse: {str(e)}")
                else:
                    st.error("Please enter a horse name")

    with col2:
        st.header("📊 Race Summary")
        
        if st.session_state.horses:
            st.metric("Horses Entered", len(st.session_state.horses))
            st.metric("Field Size", field_size)
            st.metric("Track Condition", track_condition)
            
            st.subheader("🐎 Current Entries:")
            for i, horse in enumerate(st.session_state.horses, 1):
                st.write(f"{i}. **{horse['name']}**")
                st.caption(f"   Speed: {horse['beyer_speed_figure']} | Post: {horse['post_position']}")
        else:
            st.info("👆 Add horses using the form")

    # Prediction section
    if st.session_state.horses and len(st.session_state.horses) >= 2:
        st.header("🔮 AI Predictions")
        
        predictor = HorseRacingPredictor()
        predictions = predictor.predict_race(st.session_state.horses)
        
        st.subheader("🏆 Top 5 Predictions")
        
        col_pred1, col_pred2 = st.columns([1, 1])
        
        with col_pred1:
            # Create a nice table
            display_df = pd.DataFrame(predictions)
            st.dataframe(display_df.head(5)[['Horse', 'Win_Probability', 'Score', 'Beyer_Figure']])
        
        with col_pred2:
            # Simple bar chart using Streamlit's built-in chart
            chart_data = pd.DataFrame({
                'Horse': [p['Horse'] for p in predictions[:5]],
                'Win Probability': [p['Win_Probability'] for p in predictions[:5]]
            })
            st.bar_chart(chart_data.set_index('Horse'))

        # Detailed analysis
        with st.expander("📈 Detailed Analysis"):
            for idx, horse in enumerate(predictions[:5], 1):
                col_anal1, col_anal2 = st.columns([1, 2])
                
                with col_anal1:
                    st.subheader(f"{idx}. {horse['Horse']}")
                    st.metric("Win Probability", f"{horse['Win_Probability']}%")
                    st.metric("Score", horse['Score'])
                
                with col_anal2:
                    st.write("**Performance Metrics:**")
                    st.write(f"• Beyer Figure: {horse['Beyer_Figure']:.1f}")
                    st.write(f"• Recent Form: {horse['Form_Score']:.3f}")
                    st.write(f"• Class Score: {horse['Class_Score']:.3f}")
                    st.write(f"• Jockey Score: {horse['Jockey_Score']:.3f}")
                    st.write(f"• Trainer Score: {horse['Trainer_Score']:.3f}")
                    st.write(f"• Post Advantage: {horse['Post_Advantage']:.3f}")
                    st.write(f"• **Analysis:** {horse['Analysis']}")
                
                st.divider()

        # Betting recommendations
        st.header("💰 Betting Strategy")
        
        col_bet1, col_bet2, col_bet3 = st.columns(3)
        
        with col_bet1:
            favorite = predictions[0]
            st.metric("🏆 Favorite", favorite['Horse'], f"{favorite['Win_Probability']}%")
        
        with col_bet2:
            if len(predictions) > 1:
                value_play = predictions[1] if predictions[1]['Win_Probability'] > 10 else predictions[0]
                st.metric("💎 Value Play", value_play['Horse'], f"{value_play['Win_Probability']}%")
        
        with col_bet3:
            if len(predictions) > 2:
                longshot = predictions[-1] if predictions[-1]['Win_Probability'] < 10 else predictions[2]
                st.metric("🚀 Longshot", longshot['Horse'], f"{longshot['Win_Probability']}%")

        # Export functionality
        st.header("📁 Export Results")
        
        # Convert to CSV
        csv_data = []
        for horse in predictions:
            csv_data.append({
                'Rank': predictions.index(horse) + 1,
                'Horse': horse['Horse'],
                'Win_Probability': horse['Win_Probability'],
                'Score': horse['Score'],
                'Beyer_Figure': horse['Beyer_Figure'],
                'Analysis': horse['Analysis']
            })
        
        csv_df = pd.DataFrame(csv_data)
        csv = csv_df.to_csv(index=False)
        
        st.download_button(
            label="📊 Download Predictions CSV",
            data=csv,
            file_name=f"horse_racing_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # Clear button
        if st.button("🗑️ Clear All Horses", type="secondary"):
            st.session_state.horses = []
            st.rerun()
        
    elif len(st.session_state.horses) < 2 and len(st.session_state.horses) > 0:
        st.info("🐎 Add at least 2 horses to generate AI predictions!")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🏇 Powered by KimiK2 AI Horse Racing Analysis System</p>
        <p>Analysis includes: Speed figures, recent form, class levels, jockey/trainer stats, and post position</p>
        <p>Remember: This is for entertainment purposes. Always gamble responsibly.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
