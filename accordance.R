# load all result files
# samples should be ordered. 

# # To generate the ref file, something like
# ref = nar.02838.met.k.2014.File005[3:nrow(nar.02838.met.k.2014.File005), grep(pattern = ".*reference", nar.02838.met.k.2014.File005[2, ])]
# ref = head(ref, -2) #watch out for last 2 lines!
# rownames(ref) =  nar.02838.met.k.2014.File005[3:nrow(nar.02838.met.k.2014.File005), 1]
# make.names(nar.02838.met.k.2014.File005[2, grep(pattern = ".*reference", nar.02838.met.k.2014.File005[2, ])], unique = T)
# colnames(ref) = make.names(nar.02838.met.k.2014.File005[2, grep(pattern = ".*reference", nar.02838.met.k.2014.File005[2, ])], unique = T)


ref <- read.table("/vol/cs02/scratch/cmessers/projects/BIH/HLA/ref.csv", header=TRUE, quote="\"")
bwakit <- read.table("/vol/cs02/scratch/cmessers/projects/BIH/HLA/bwakit", quote="\"")
hlassign <- read.table("/vol/cs02/scratch/cmessers/projects/BIH/HLA/hlassign", quote="\"")
optitype <- read.table("/vol/cs02/scratch/cmessers/projects/BIH/HLA/optitype", quote="\"")

typer = c("optitype", 'bwakit', "hlassign")

#get consensus from ref
samples=bwakit[,1]

# sort acc. to results
xref = ref[match(samples, rownames(ref)), 1:6]

acc = matrix(0, nrow=length(samples), ncol = 4)
rownames(acc) = samples
colnames(acc) = c(typer, "possible 4digit hits")

for (refrow in 1:nrow(xref)){
# for (refrow in 6){
  hlatype = c()
  # for(refcol in 1:ncol(xref)){
  for(refcol in 1:6){
    hlatype = append(hlatype, gsub(pattern = "(^[ABC]\\*[0-9]{2}:[0-9]{2,3}).*", replacement = '\\1', xref[refrow, refcol]))
    
    if (nchar(xref[refrow,refcol]) >= 7){
      acc[refrow, 4] = acc[refrow, 4] + 1
    }
    
    for (method in 1:length(typer)){          
      hlaprediction = c()
      for(refcol in 1:6){
        hlaprediction = append(hlaprediction, gsub(pattern = "(^[ABC]\\*[0-9]{2}:[0-9]{2,3}).*", replacement = '\\1', get(typer[method])[refrow, refcol+1]))
        # print(c(hlaprediction, hlatype, sum(hlaprediction %in% hlatype)))
        acc[refrow, method] = sum(hlaprediction %in% hlatype)
      }
    }      
  }
}
