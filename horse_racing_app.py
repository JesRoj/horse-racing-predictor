import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="🐎 PDF-Only Racing Predictor", 
    page_icon="🐎",
    layout="wide"
)

# Remove manual input completely - PDF only
st.markdown("""
<style>
/* Hide manual input sections */
div[data-testid="stTextArea"], 
div[data-testid="stButton"] button[kind="primary"]:contains("Analyze Manual Input") {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

class RacingPredictorPDFOnly:
    def __init__(self):
        self.weights = {
            'speed_figure': 0.30, 'recent_form': 0.25, 'class_level': 0.15,
            'post_position': 0.10, 'jockey_skill': 0.10, 'trainer_stats': 0.08,
            'distance_fitness': 0.02
        }
        
        self.post_weights = {
            1: 0.98, 2: 0.99, 3: 1.00, 4: 0.99, 5: 0.98,
            6: 0.97, 7: 0.96, 8: 0.94, 9: 0.92, 10: 0.90,
            11: 0.87, 12: 0.84, 13: 0.81, 14: 0.78, 15: 0.75,
            16: 0.72, 17: 0.69, 18: 0.66, 19: 0.63, 20: 0.60
        }

    def calculate_score(self, horse_data):
        speed_base = horse_data.get('speed_rating', 75)
        recent_form = horse_data.get('recent_finishes', [5, 5, 5])
        form_score = 0.5
        if recent_form and len(recent_form) > 0:
            total = sum(recent_form)
            avg = total / len(recent_form)
            form_score = max(0, (10 - avg) / 10)
        post = horse_data.get('post_position', 5)
        post_score = self.post_weights.get(post, 0.90)
        return speed_base * 0.5 + form_score * 40 + post_score * 10

    def predict_race(self, horses_data):
        results = []
        for horse in horses_data:
            score = self.calculate_score(horse)
            results.append({
                'Horse': horse.get('name', 'Unknown'),
                'Score': round(score, 2),
                'Win_Probability': round(max(0, score - 70), 1),
                'Post_Position': horse.get('post_position', '?'),
                'Weight': horse.get('weight', '?'),
                'Recent_Form': horse.get('recent_finishes', '?'),
                'Analysis': "📊 Racing analysis"
            })
        
        results.sort(key=lambda x: x['Score'], reverse=True)
        total_prob = sum([r['Win_Probability'] for r in results])
        
        if total_prob > 0:
            for result in results:
                result['Win_Probability'] = round((result['Win_Probability'] / total_prob * 100), 1)
        else:
            for result in results:
                result['Win_Probability'] = round((100.0 / len(results)), 1)
        
        return results

def extract_racing_data_pdf_only(text):
    """PDF-only racing data extraction - no manual fallback"""
    horses = []
    lines = text.strip().split('\n')
    
    # Quality check first
    if not lines or len(lines) < 3:
        return []  # Empty if no meaningful content
    
    # Clean and process
    clean_text = text.encode('ascii', 'ignore').decode('ascii')
    clean_text = clean_text.replace('obj', '').replace('PDF', '')
    clean_text = clean_text.replace('³', '3').replace('²', '2').replace('¹', '1')
    clean_text = clean_text.replace('½', '0.5').replace('¼', '0.25').replace('¾', '0.75')
    
    # Simple extraction
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or len(line) < 5:
            continue
            
        words = line.split()
        horse_name = ""
        numbers = []
        
        for word in words:
            word = word.strip('.,;[](){}')
            
            # Try as number
            try:
                if '.' in word:
                    num = float(word)
                    if num == int(num):
                        numbers.append(int(num))
                else:
                    num = int(word)
                    numbers.append(num)
            except ValueError:
                # It's text - use as name if reasonable
                if (word.isalpha() and 
                    len(word) >= 3 and 
                    len(word) <= 20 and
                    not horse_name and
                    word.lower() not in ['pdf', 'obj', 'endobj']):
                    horse_name = word
        
        if horse_name and len(numbers) >= 1:
            horse_data = {
                'name': horse_name,
                'post_position': len(horses) + 1,
                'weight': numbers[0] if 10 <= numbers[0] <= 70 else 55,
                'recent_finishes': numbers[1:4] if len(numbers) > 1 else [5, 5, 5],
                'jockey_win_percentage': 0.12,
                'trainer_win_percentage': 0.15,
                'field_size': len([l for l in lines if len(l.strip()) > 5]),
                'race_distance': 8.0,
                'track_condition': 'fast',
                'speed_rating': 75
            }
            horses.append(horse_data)
    
    return horses[:20]  # Max 20 horses

def main():
    st.title("🏇 PDF-Only Racing Predictor")
    st.subheader("📄 Racing Document Analysis Only")

    # Race setup
    with st.sidebar:
        st.header("🏁 Race Setup")
        race_name = st.text_input("Race Name/Track", "Universal Race")
        distance = st.number_input("Distance (furlongs)", 5.0, 14.0, 8.0, 0.5)
        surface = st.selectbox("Surface", ["Dirt", "Turf", "All-Weather"])

    # Main content - PDF Only
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("📄 Upload Racing Document Only")
        
        st.markdown("""
        ### 📄 PDF-Only Processing:
        - **Racing programs** (PDF format)
        - **Text files** (.txt, .csv)
        - **Racing cards** (any format)
        - **No manual input** - file upload only
        - **Automatic processing** - upload and analyze
        """)

        # File upload - PDF only
        uploaded_file = st.file_uploader(
            "📁 Upload racing document (PDF, TXT, CSV only)",
            type=['pdf', 'txt', 'csv'],
            help="Upload racing documents only - no manual input"
        )

        if uploaded_file is not None:
            with st.spinner("🔍 Processing racing document..."):
                text_content = ""
                try:
                    # Read with multiple encoding attempts
                    content = uploaded_file.read()
                    for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                        try:
                            text_content = content.decode(encoding)
                            break
                        except:
                            continue
                    
                    if text_content:
                        st.success("✅ File read successfully!")
                        
                        # Show preview
                        with st.expander("👀 Preview extracted text"):
                            preview = text_content[:300] + "..." if len(text_content) > 300 else text_content
                            st.text(preview)
                        
                        # Extract racing data
                        horses = extract_racing_data_pdf_only(text_content)
                        
                        if horses:
                            st.success(f"🐎 Found {len(horses)} horses!")
                            
                            # Show extracted horses
                            with st.expander("📋 View extracted horses"):
                                for i, horse in enumerate(horses, 1):
                                    col_h1, col_h2 = st.columns([1, 1])
                                    with col_h1:
                                        st.write(f"**{i}. {horse['name']}**")
                                        st.caption(f"Post: {horse['post_position']} | Weight: {horse['weight']}kg")
                                    with col_h2:
                                        st.caption(f"Recent: {horse['recent_finishes']}")
                            
                            if st.button("🚀 Analyze Race", type="primary"):
                                st.session_state.horses = horses
                                st.rerun()
                        else:
                            st.warning("⚠️ Could not extract horse data from this file format.")
                            st.info("💡 Try converting your PDF using Google Drive or online OCR tools first.")
                    else:
                        st.error("❌ Could not read file content.")
                        
                except Exception as e:
                    st.error(f"❌ File error: {str(e)}")

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
            st.info("📄 Upload a racing document to analyze")

    # AI Analysis Section
    if 'horses' in st.session_state and len(st.session_state.horses) >= 2:
        st.header("🔮 AI Race Analysis")
        
        predictor = RacingPredictorPDFOnly()
        
        # Update with race conditions
        for horse in st.session_state.horses:
            horse['race_distance'] = distance
            horse['track_condition'] = surface.lower().replace('-', '_')
            horse['field_size'] = len(st.session_state.horses)
        
        predictions = predictor.predict_race(st.session_state.horses)
        
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

        # Fixed CSV Export
        st.header("📁 Export Predictions")
        
        # Create proper CSV content
        csv_lines = ["Rank,Horse,Post_Position,Win_Probability,Score,Weight,Recent_Form,Analysis"]
        
        for i, horse in enumerate(predictions, 1):
            # Clean the data for CSV
            horse_name = horse['Horse'].replace(',', ' ').replace('"', '').strip()
            recent_form = str(horse['Recent_Form']).replace(',', ' ')
            
            csv_line = f"{i},{horse_name},{horse['Post_Position']},{horse['Win_Probability']},{horse['Score']},{horse['Weight']},\"{recent_form}\",\"{horse['Analysis']}\""
            csv_lines.append(csv_line)
        
        csv_content = "\n".join(csv_lines)
        
        st.download_button(
            label="📊 Download Predictions CSV",
            data=csv_content,
            file_name=f"race_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    # Footer - PDF Only
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🏇 PDF-Only Racing AI - File Upload Only</p>
        <p>No manual input • File upload only • Automatic processing</p>
        <p><strong>Remember:</strong> This is for entertainment purposes. Always gamble responsibly.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
