# Get arguments from command line/python
args <- commandArgs(trailingOnly = TRUE)
save_directory <- (args[[1]])
file_name_data <- args[[2]]
file_name_fallspeed <- file.path(save_directory, "temp_fallspeeds.csv")
file_name_lookup <- file.path(save_directory, "temp_PollenLookup.csv")

# import data
load(file_name_data)
lookup_fallspeed <- read.csv(file_name_fallspeed)
lookup_pollen <- read.csv(file_name_lookup) 

for (taxon in 1:nrow(lookup_fallspeed)){
  fall_speed_class <- 100 * round(lookup_fallspeed[taxon, 2], 2) + 1 # not sure about this +1
  fall_speed_class[fall_speed_class<2] <- 2
  pollen_lookup_ring<- predict(lsm_unstable[[fall_speed_class]], lookup_pollen$distance)
  ring_conversion_factor<- (0.5/ (pi*lookup_pollen$distance))
  pollen_lookup <-  ring_conversion_factor * pollen_lookup_ring
  lookup_pollen[[paste0(lookup_fallspeed$taxon[taxon],"_DW")]]<- pollen_lookup
} 
write.csv(lookup_pollen, file.path(save_directory, "temp_PollenLookup2.csv"), row.names = FALSE)

