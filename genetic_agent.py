#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 16:13:27 2020

@author: stan
"""
import numpy as np

class GeneticAgent(object):
    """
    old_generation is a list of vector, reward pairs
    """
    def __init__(self, p_mutation, p_crossover, p_replication, diversity_factor,
                 max_mutations, max_cross, coordinate_range, reward_th):
        np.random.seed()
        # Probabilities of mutation, crossover and replication
        self.p_mutation = p_mutation 
        self.p_crossover = p_crossover 
        self.p_replication = p_replication 
        # Diversity factor - sets how much diversity is preferred over highest
        # reward
        self.diversity_factor = diversity_factor
        # Maximum number of mutations and fields that are crossed over
        self.max_mutations = max_mutations
        self.max_cross = max_cross
        # Limits on each entry in the array
        self.coordinate_range = coordinate_range
        # Threshold on the reward when to stop forcing diversity
        self.reward_th = reward_th 
        
    def get_new_generation(self, old_generation):
        # sorts the generation by reward it got
        # -1 is to sort it in descending order
        old_generation = old_generation[((-1)*old_generation[:,1]).argsort()]
        # always copy the top performer
        old_vectors = list(old_generation[:,0])
        new_generation = np.array([old_generation[0][0]])
        # when reached high reward for an extended period, stop forcing diversity
        if old_generation[0][1] > self.reward_th:
            self.diversity_factor = 0
        while len(new_generation)!=len(old_generation):
            # Randomly choose the genetic alteration applied
            genetic_type = np.random.choice(['mut', 'cross', 'repl'], 
                                            p=[self.p_mutation, 
                                               self.p_crossover,
                                               self.p_replication])
            # Find vector choice probabilities based on rewards and diversity
            vec_choice_probabilities = list(self.get_choice_probabilities(old_generation,
                                                                     new_generation))
            
            # Choose 2 vectors for the next genetic operation - possibly only
            # one of them will be used
            vec1_idx, vec2_idx = np.random.choice(len(old_vectors), size=2, replace=False, p=vec_choice_probabilities)
            vec1 = old_vectors[vec1_idx]
            vec2 = old_vectors[vec2_idx]
            
            if genetic_type=='mut':
                #print('mutating')
                new_generation = np.concatenate((new_generation, [self.apply_mutation(vec1)]))
            if genetic_type=='repl':
                #print('replicating')
                new_generation = np.concatenate((new_generation, [vec1]))
            if genetic_type=='cross':
                #print('crossing')
                vec1, vec2 = self.apply_crossover(vec1, vec2)
                new_generation = np.concatenate((new_generation, [vec1]))
                if len(new_generation)<len(old_generation):
                    new_generation = np.concatenate((new_generation, [vec2]))
            
        return new_generation
    
    def measure_diversity(self, vec, vec_list):
        # measure average euclidean distance from a vector to the list of 
        # already chosen vectors - ensures exploration
        distances = []
        for y in vec_list:
            distances.append(np.linalg.norm(vec-y))
        diversity = np.average(distances)
        return diversity
    
    def get_choice_probabilities(self, old_generation, new_generation):
        # list of the second element
        rewards = old_generation[:,1]
        diversified_rewards = rewards + np.array([self.measure_diversity(vec, new_generation)*
                                                  self.diversity_factor for vec in old_generation[:,0]])
        probabilities = diversified_rewards/np.sum(diversified_rewards)
        return probabilities
    
    def apply_mutation(self, vec):
        # Get the number of fields to mutate
        no_mutations = np.random.randint(1, self.max_mutations+1)
        # Get the indices of the fields to mutate
        idx_to_mutate = np.random.choice(len(vec), no_mutations, replace=False)
        # Mutation is changing a value of a field to a random value 
        # Coordinate ranges hold the range that variable can take, bounded to 
        # accelerate learning
        for idx in idx_to_mutate:
            coordinate_range = self.coordinate_range[idx]
            vec[idx] = np.random.sample()*(coordinate_range[1]-coordinate_range[0])+coordinate_range[0]
        return vec
    
    def apply_crossover(self, vec1, vec2):
        # Get the number of fields to cross over
        no_cross = np.random.randint(1, self.max_cross+1)
        # Get the indices of the fields to cross over
        idx_to_cross = np.random.choice(len(vec1), no_cross, replace=False)
        for idx in idx_to_cross:
            temp = vec1[idx]
            vec1[idx] = vec2[idx]
            vec2[idx] = temp
        return vec1, vec2
    
    def get_nearby_trajectory(self, vec, idx1=0, idx2=-1):
        # Modify the trajectory between given indices
        new_trajectory = (np.random.random()*0.1+0.95)*vec
        return new_trajectory
    
def main():
    geneticAgent = GeneticAgent(0.3, 0.5, 0.2, 1.0, 1, 1, [[0, 1], [0, 1]], 10)
    old_generation = np.array([[[0.2, 0.7], 5], [[0.1, 0.8], 5], [[0.3, 0.4],5]])
    new_generation = geneticAgent.get_new_generation(old_generation)
    print(new_generation)
    
if __name__=='__main__':
    main()
    
