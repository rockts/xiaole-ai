"""测试对话质量增强功能"""

from dialogue_enhancer import DialogueEnhancer


def test_emotion_detection():
    """测试情感识别"""
    enhancer = DialogueEnhancer()
    
    tests = [
        ("今天太开心了！", "joy"),
        ("我很难过", "sadness"),
        ("真让人生气", "anger"),
        ("有点担心", "fear"),
        ("竟然是这样", "surprise"),
    ]
    
    print("🧪 情感识别测试:")
    for text, expected in tests:
        detected = enhancer.detect_emotion(text)
        status = "✅" if detected == expected else "⚠️"
        print(f"  {status} '{text}' -> {detected} (期望:{expected})")
    

def test_empathy_response():
    """测试共情回复"""
    enhancer = DialogueEnhancer()
    
    response = "好的，我明白了"
    
    print("\n🧪 共情回复测试:")
    for emotion in ['joy', 'sadness', 'anger']:
        enhanced = enhancer.add_empathy_prefix(emotion, response)
        print(f"  {emotion}: {enhanced}")


def test_style_consistency():
    """测试风格一致性"""
    enhancer = DialogueEnhancer()
    
    response = "其实我觉得这个问题挺好的，大概需要仔细考虑一下。"
    
    print("\n🧪 风格一致性测试:")
    for style in ['concise', 'balanced', 'professional']:
        styled = enhancer.ensure_style_consistency(response, style)
        print(f"  {style}: {styled}")


def test_full_enhancement():
    """测试完整增强"""
    enhancer = DialogueEnhancer()
    
    user_input = "今天好开心啊！"
    response = "好的"
    history = [{"role": "user", "content": "你好"}]
    
    enhanced = enhancer.enhance_response(
        response, user_input, history, style='balanced'
    )
    
    print(f"\n🧪 完整增强测试:")
    print(f"  输入: {user_input}")
    print(f"  原回复: {response}")
    print(f"  增强后: {enhanced}")


if __name__ == '__main__':
    test_emotion_detection()
    test_empathy_response()
    test_style_consistency()
    test_full_enhancement()
    print("\n✅ 所有测试完成！")
