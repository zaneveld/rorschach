import unittest
import pandas as pd
from pandas.testing import assert_frame_equal
from numpy import array
from copy import deepcopy
from random import choice
#Import our functions that we want to test
from narrative_object import NarrativeObject,UniformRandomGenerator
from associations import Associations
from generators import region_name_generator

class TestNarrativeObject(unittest.TestCase):
    def setUp(self):
        """Set up some example associations for testing"""
        #Example: Coral Coast Goblin
        #Set up some associations for Sneaky or Oceanic entitites
        array_map = {"espionage":0,"magic":1,"size":2,\
          "violent":3,"strength":4,"ocean":5,"witches":6}
        sneaky_assoc = {"espionage":25,"magic":25,"size":-5}
        water_assoc = {"ocean":25}
        antimagic = {"magic":-25}
        
        self.SneakyEntityAssoc = Associations(assoc_dict = sneaky_assoc,\
          assoc_array_map = array_map,assoc_type='Entity')
        
        self.CoralCoastEntityAssoc = Associations(assoc_dict = water_assoc,\
          assoc_array_map = array_map, assoc_type='Entity') 

        self.AntiMagicEntityAssoc = Associations(assoc_dict = antimagic,\
          assoc_array_map = array_map,assoc_type = 'Entity')
        
        self.AntiMagicSettingAssoc = Associations(assoc_dict = {"witches":25,\
          "magic":25},assoc_array_map = array_map,assoc_type = 'Setting')
        
        self.PearlDaggerEntityAssoc = Associations(assoc_dict = {"espionage":25,\
          "ocean":25},assoc_array_map = array_map,assoc_type = 'Entity')
 
        #Set up some gameplay associations
        array_map = {"aggro":0,"small_creatures":1}
        game_assoc = {"aggro":25,"small_creatures":25}

        self.GameAssoc = Associations(assoc_dict = game_assoc,\
          assoc_array_map = array_map,assoc_type='Game')

        #Build up a list of all the associations
        self.AllAssociations = [self.SneakyEntityAssoc,\
          self.CoralCoastEntityAssoc,self.GameAssoc]

        self.WitchhuntersCloak = NarrativeObject(qualities = {"card_name":"Witchhunter's Cloak"},
          narrative_type = "Object",required_qualities=[],\
          associations = [self.AntiMagicEntityAssoc,self.AntiMagicSettingAssoc],\
          generator=UniformRandomGenerator(data = [None]))

        self.PowerToughnessGenerator = UniformRandomGenerator(data = list(range(1,12)))
        
        self.Goblin = NarrativeObject(qualities = {"card_name":"Coral Coast Goblin"},\
          narrative_type = "Creature",\
          required_qualities=[],\
          associations = [],\
          target_associations = self.AllAssociations,\
          generator = self.PowerToughnessGenerator.generate)     
  
        self.PearlDagger = NarrativeObject(qualities = {"card_name":"Pearl Dagger"},
          narrative_type = "Object",required_qualities=[],\
          associations = [self.PearlDaggerEntityAssoc],\
          target_associations = [self.PearlDaggerEntityAssoc],\
          generator=UniformRandomGenerator(data = [None]))

    def test_toPandas_serializes_a_narrative_object_to_dataframe(self):
        """NarrativeObject.toPandas serializes self to dataframe"""
        obs = self.Goblin.toPandas("Goblin","Entity")
        self.assertTrue(type(obs) == pd.DataFrame)
        obs.to_csv("goblin_test.tsv",sep="\t")        


    def test_toPandas_and_fromPandas_round_trip_data(self):
        """NarrativeObject.fromPandas and NarrativeObject.toPandas round trip data"""
        df = self.Goblin.toPandas("Goblin","Entity")

        obs_narr_obj = NarrativeObject.fromPandas(df,qualities={},generator=
          UniformRandomGenerator(range(10)))
        obs_df = obs_narr_obj.toPandas()
        print("starting dataframe:\n",df.iloc[:,1:])
        print("final dataframe:\n",obs_df.iloc[:,1:])
        assert_frame_equal(df.iloc[:,1:],obs_df.iloc[:,1:])

    def test_score_compares_categories_of_associations(self):
        """NarrativeOBject.score compares categories"""
        obs1 = self.Goblin.score(self.WitchhuntersCloak)
        obs2 = self.Goblin.score(self.PearlDagger)
        self.assertTrue(obs2 > obs1)

    def test_score_returns_50percent_if_no_target_associations_are_in_other(self):
        """NarativeObject.score returns 0.0 if self.TargetAssociations doesn't overlap with other.Associations"""
        obs = self.PearlDagger.score(self.WitchhuntersCloak)
        exp = 0.50
        self.assertEqual(round(obs,3),round(exp,3))

    def test_association_dict_functions_with_valid_data_in_overwrite_mode(self):
        """NarrativeObject.associationsDictFromList functions in overwrite mode"""
        obs = self.Goblin.associationsDict(self.AllAssociations,merge_mode="overwrite")
        exp = {"Entity":self.CoralCoastEntityAssoc,"Game":self.GameAssoc}
        self.assertEqual(obs,exp)

    def test_init_averages_nonzero_associations__in_the_same_category(self):
        """__init__ averages nonzero_associations within the same category"""
        obs = self.Goblin.TargetAssociations['Entity'].AssocDict
        exp = {"espionage":25,"magic":25,"size":-5.0,"ocean":25,"violent":0.0,"strength":0.0,"witches":0.0}
        self.assertEqual(obs,exp)
 
    def test_init_sorts_associations_by_type_with_valid_input(self):
        """__init__ sorts associations_by_type with valid input"""
        obs = sorted(self.Goblin.TargetAssociations.keys())
        exp = ['Entity','Game']
        self.assertEqual(obs,exp)
    
    def test_init_keeps_associations_empty_if_none_provided(self):
        """__init__ sorts associations_by_type with valid input"""
        obs = sorted(self.Goblin.Associations.keys())
        exp = []
        self.assertEqual(obs,exp) 
    
    def test_get_returns_existing_quality_if_present(self):
        """NarrativeObject.get() returns existing quality"""
        obs = self.Goblin.get("card_name")
        exp = "Coral Coast Goblin"
        self.assertEqual(obs,exp)

    def test_get_returns_new_quality(self):
        """NarrativeObject.get() uses default generator to get new qualities"""
        obs = self.Goblin.get('Power') 
        self.assertTrue(obs in list(range(1,12)))
        obs = self.Goblin.get('Toughness') 
        self.assertTrue(obs in list(range(1,12)))

    def test_get_saves_new_qualities(self):
        """NarrativeObject.get() uses default generator to get new qualities"""
        obs1 = self.Goblin.get('Power') 
        obs2 = self.Goblin.get('Power')
        
        self.assertEqual(obs1,obs2)

    def test_getitem_calls_get(self):
        """NarrativeObject[quality] gets or generates a quality"""
        obs = self.Goblin['card_name']
        exp = "Coral Coast Goblin"
        self.assertEqual(obs,exp)

    def test_get_uses_specialty_generators_if_provided(self):
        """NarrativeObject.get uses specialty generators if provided"""
        self.Goblin.SpecialtyGenerators["homeland"]=region_name_generator
        result = self.Goblin.get("homeland")
        print("RESULT:",result)
        #self.assertTrue("The " in result)
        #self.assertTrue("of" in result)

    def test_update_associations_from_qualities_updates_associations(self):
        """NarrativeObject.updateAssociationsFromQualities functions with valid input"""
        
        self.Goblin.Qualities["item"]=self.WitchhuntersCloak
        self.Goblin.updateAssociationsFromQualities(merge_mode="weighted_average")
        
        obs = self.Goblin.Associations["Setting"]["witches"]
        exp = 25
        self.assertEqual(obs,exp)
        
    def test_update_associations_from_qualities_uses_weights_for_weighted_averages(self):
        """NarrativeObject.updateAssociationsFromQualities weights qualities given weights"""
        self.Goblin.Associations = self.Goblin.TargetAssociations        
        
        print("[PRE] Goblin associations:",self.Goblin.Associations)
        self.Goblin.Qualities["item"]=self.WitchhuntersCloak
        weights = {"item":0.50}
        self.Goblin.updateAssociationsFromQualities(weights=weights)
        
        obs = self.Goblin.Associations["Entity"]["magic"]
        exp = 0.0 #25*0.5 + -25.0*0.5
        self.assertEqual(obs,exp)
        

    def test_narrative_object_loads_associations_from_file(self):
        """NarrativeObject.fromPandas loads associations from a file"""
        df = pd.read_csv("../data/associations.txt",sep="\t")
        
#Run the tests
unittest.main()
