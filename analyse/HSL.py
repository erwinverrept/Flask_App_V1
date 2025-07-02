def rgb_to_hsl(r, g, b):
    """
    Zet RGB-waarden (0-255) om naar HSL (Hue, Saturation, Lightness).
    Retourneert een string 'hsl(H, S%, L%)'
    """
    r, g, b = [x / 255.0 for x in (r, g, b)]
    mx = max(r, g, b)
    mn = min(r, g, b)
    l = (mx + mn) / 2
     

    if mx == mn:
        h = s = 0
    else:
        d = mx - mn
        s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
        if mx == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif mx == g:
            h = (b - r) / d + 2
        else:
            h = (r - g) / d + 4
        h /= 6

    h = int(round(h * 360))
    s = int(round(s * 100))
    l = int(round(l * 100))
    #H_percentage = int(round((h / 360) * 100))
    return f"({h}, {s}%, {l}%)"