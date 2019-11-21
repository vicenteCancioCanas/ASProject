from operator import itemgetter
from math import pow, sqrt
from scipy.stats import pearsonr


class Algorithm:

    def __init__(self, matrix):
        self.matrix = matrix

    # Calculate the PC between 2 users, given their index in the matrix (u and v)
    def pc(self, u, v):
        n_items = len(self.matrix[0])
        n_users = len(self.matrix)

        # Ratings of items rated by both users
        ratings_u = []
        ratings_v = []
        for i in range(n_items):
            ru = self.matrix[u][i]
            rv = self.matrix[v][i]

            if (ru != 0 and rv != 0):
                ratings_u.append(ru)
                ratings_v.append(rv)

        # Mean of ratings given by user u (items rated by both users)
        mean_u = 0
        for i in ratings_u:
            mean_u += i
        mean_u /= len(ratings_u)

        # Mean of ratings given by user v (items rated by both users)
        mean_v = 0
        for i in ratings_v:
            mean_v += i
        mean_v /= len(ratings_v)

        # Calculation of PC
        up = 0
        for i in range(len(ratings_u)):
            up += (ratings_u[i] - mean_u) * (ratings_v[i] - mean_v)

        down1 = 0
        for ru in ratings_u:
            v = (ru - mean_u)
            down1 += pow(v, 2)

        down2 = 0
        for rv in ratings_v:
            v = (rv - mean_v)
            down2 += pow(v, 2)

        down = sqrt(down1 * down2)

        # If the denominator is 0, return 1 (higher value of PC)
        return 1 if down == 0 else up/down

    def pclib(self, u, v):
        n_items = len(self.matrix[0])
        n_users = len(self.matrix)

        # Ratings of items rated by both users
        ratings_u = []
        ratings_v = []
        for i in range(n_items):
            ru = self.matrix[u][i]
            rv = self.matrix[v][i]

            if (ru != 0 and rv != 0):
                ratings_u.append(ru)
                ratings_v.append(rv)

        return pearsonr(ratings_u, ratings_v)

    # u is the index of the user (not included in the results because it's not a neighbor of his self)
    # i is the index of the item (movie)
    # k is the limit of neighbors (lower or equal than 49)
    # return a list of tuples, where the first value is the index of the neighbor and the second the PC between the user u and that neighbor
    # Note: The size of the retuned list could be lower than k
    def neighbors(self, u, i, k):
        n_users = len(self.matrix)
        neighbors = []
        for v in range(n_users):
            if (v != u and self.matrix[v][i] != 0):
                neighbors.append((v, self.pc(u, v)))
        neighbors.sort(key=itemgetter(1), reverse=True)
        return neighbors[0:k]

    def rating_average(self, ratings):
        n_items = len(ratings)
        rated_by_u = 0
        for i in range(n_items):
            if (ratings[i] != 0):
                rated_by_u += 1
        return sum(ratings) / rated_by_u

    def predicted_rating(self, user, item, neighbors, maxval, minval):
        # Calculate the average of the ratings of the user u
        rating_u_average = self.rating_average(self.matrix[user])

        # copy the matrix so we can normalize its values
        matrix = [[self.matrix[x][y] for y in range(
            len(self.matrix[0]))] for x in range(len(self.matrix))]
        # normalize matrix
        for v in range(len(matrix)):
            rating_v_average = self.rating_average(self.matrix[v])
            for i in range(len(matrix[v])):
                if matrix[v][i] != 0:
                    matrix[v][i] = matrix[v][i] - rating_v_average

        top_sum = 0
        bottom_sum = 0

        for neighbor in neighbors:
            v, wuv = neighbor
            h_rvi = matrix[v][item]
            top_sum += wuv * h_rvi
            bottom_sum += abs(wuv)

        predicted_rating = (top_sum / bottom_sum) + rating_u_average
        return (user, item, max(min(round(predicted_rating*2)/2, maxval),minval))
