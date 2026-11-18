"""Manual numerical algorithms: no NumPy/SciPy filtering, sorting or reductions."""


class UniformRNG:
    """Park-Miller PRNG with Schrage arithmetic (period 2**31 - 2).

    Used for reproducible educational simulation, not security.
    """

    def __init__(self, seed):
        self.state = int(seed) % 2147483647
        if self.state == 0:
            self.state = 1

    def random(self):
        hi = self.state // 127773
        lo = self.state % 127773
        value = 16807 * lo - 2836 * hi
        if value <= 0:
            value += 2147483647
        self.state = value
        return self.state / 2147483647.0


def shape(image):
    if not image or not image[0]:
        raise ValueError("Image must be nonempty.")
    width = len(image[0])
    for row in image:
        if len(row) != width:
            raise ValueError("Image rows must have the same length.")
        for value in row:
            if not (-float('inf') < value < float('inf')):
                raise ValueError("Image contains NaN or infinity.")
    return len(image), width


def mean(image):
    height, width = shape(image)
    total = 0.0
    for row in image:
        for value in row:
            total += value
    return total / (height * width)


def moments(image):
    mu = mean(image)
    total = 0.0
    count = 0
    for row in image:
        for value in row:
            total += (value - mu) ** 2
            count += 1
    return mu, (total / count) ** 0.5


def add_uniform_noise(image, fraction, seed, interpretation="std"):
    """Return noisy image, realized noise and requested standard deviation.

    std: sigma = fraction * band mean; half-width = sqrt(3) * sigma.
    half-width: half-width = fraction * band mean; sigma = half-width/sqrt(3).
    Do not clip or round: that would change the requested noise distribution.
    """
    mu = mean(image)
    if mu <= 0 or fraction < 0:
        raise ValueError("Require a positive band mean and nonnegative noise fraction.")
    if interpretation not in ("std", "half-width"):
        raise ValueError("Unknown noise interpretation.")
    half_width = fraction * mu
    if interpretation == "std":
        half_width *= 3.0 ** 0.5
    rng = UniformRNG(seed)
    noisy, noise = [], []
    for row in image:
        noisy_row, noise_row = [], []
        for value in row:
            perturbation = (2.0 * rng.random() - 1.0) * half_width
            noise_row.append(perturbation)
            noisy_row.append(value + perturbation)
        noise.append(noise_row)
        noisy.append(noisy_row)
    return noisy, noise, half_width / (3.0 ** 0.5)


def validate_filter(window, k):
    if type(window) is not int or window < 1 or window % 2 == 0:
        raise ValueError("Window must be a positive odd integer.")
    if type(k) is not int or not 1 <= k <= window * window:
        raise ValueError("k must be an integer between 1 and window squared.")


def smooth_both(image, window, k):
    """Bandwise intensity-nearest KNN and arithmetic mean on the same window.

    The center is eligible. Nearest means smallest squared intensity difference
    from the noisy center, not spatial distance. Border replication is manual.
    A manual insertion selection retains k candidates, with row-major tie order.
    Both outputs read exclusively from the unchanged noisy image.
    """
    validate_filter(window, k)
    height, width = shape(image)
    radius = window // 2
    knn, average = [], []
    for y in range(height):
        knn_row, average_row = [], []
        for x in range(width):
            center = image[y][x]
            distances, values = [], []
            total = 0.0
            for dy in range(-radius, radius + 1):
                yy = y + dy
                if yy < 0:
                    yy = 0
                elif yy >= height:
                    yy = height - 1
                for dx in range(-radius, radius + 1):
                    xx = x + dx
                    if xx < 0:
                        xx = 0
                    elif xx >= width:
                        xx = width - 1
                    value = image[yy][xx]
                    total += value
                    if k == window * window:
                        continue
                    distance = (value - center) ** 2
                    if len(values) == k and distance >= distances[-1]:
                        continue
                    position = len(values)
                    while position > 0 and distance < distances[position - 1]:
                        position -= 1
                    distances.insert(position, distance)
                    values.insert(position, value)
                    if len(values) > k:
                        distances.pop()
                        values.pop()
            local_mean = total / (window * window)
            average_row.append(local_mean)
            if k == window * window:
                knn_row.append(local_mean)
            else:
                selected_total = 0.0
                for value in values:
                    selected_total += value
                knn_row.append(selected_total / k)
        knn.append(knn_row)
        average.append(average_row)
    return knn, average


def mse(reference, estimate):
    height, width = shape(reference)
    if shape(estimate) != (height, width):
        raise ValueError("MSE images must have identical dimensions.")
    total = 0.0
    for y in range(height):
        for x in range(width):
            total += (reference[y][x] - estimate[y][x]) ** 2
    return total / (height * width)


def summarize(values):
    if not values:
        raise ValueError("Cannot summarize an empty sequence.")
    total = 0.0
    for value in values:
        total += value
    mu = total / len(values)
    if len(values) == 1:
        return mu, 0.0
    squared = 0.0
    for value in values:
        squared += (value - mu) ** 2
    return mu, (squared / (len(values) - 1)) ** 0.5
